#! /bin/env python3

import os, sys, subprocess, time, json, requests

def log(r):
    print('{0} {1} {2} {3}'.format(r.method, r.url, r.headers, r.body))

api_key = ''
try:
    api_key = os.environ['ETHERSCAN_API_KEY']
except KeyError:
    print('''  You need an Etherscan Api Key to verify contracts.
  Create one at https://etherscan.io/myapikey

  Then export it with `export ETHERSCAN_API_KEY=xxxxxxxx'
''')
    exit()

document = ''
try:
    document = open('out/dapp.sol.json')
except FileNotFoundError:
    exit('run dapp build first')
content = json.load(document)

if len(sys.argv) not in [3, 4]:
    print('''usage:

./verify.py <contractname> <address> [constructorArgs]
''')
    exit()

contract_name = sys.argv[1]
contract_address = sys.argv[2]
if len(contract_address) !=  42:
    exit('malformed address')
constructor_arguments = ''
if len(sys.argv) == 4:
    constructor_arguments = sys.argv[3]
contract_path = ''

for path in content['contracts'].keys():
    for name in content['contracts'][path].keys():
        if name == contract_name:
            contract_path = path
if contract_path == '':
    exit('contract name not found.')

print('Obtaining chain... ')
seth_chain = subprocess.run(['seth', 'chain'], capture_output=True)
chain = seth_chain.stdout.decode('ascii').replace('\n', '')
print(chain)

text_metadata = content['contracts']['src/single.sol']['s']['metadata']
metadata = json.loads(text_metadata)

compiler_version = 'v' + metadata['compiler']['version']

evm_version = metadata['settings']['evmVersion']

optimizer_enabled = metadata['settings']['optimizer']['enabled']

optimizer_runs = metadata['settings']['optimizer']['runs']

license_name = metadata['sources']['src/single.sol']['license']

license_numbers = {
    'GPL-3.0-or-later': 5,
    'AGPL-3.0-or-later': 13
}

license_number = license_numbers[license_name]

module = 'contract'

action = 'verifysourcecode'

code_format = 'solidity-single-file'

flatten = subprocess.run([
    'hevm',
    'flatten',
    '--source-file',
    contract_path
], capture_output=True)

source_code = flatten.stdout

data = {
    'apikey': api_key,
    'module': module,
    'action': action,
    'contractaddress': contract_address,
    'sourceCode': source_code,
    'codeFormat': code_format,
    'contractName': contract_name,
    'compilerversion': compiler_version,
    'optimizationUsed': '1' if optimizer_enabled else '0',
    'runs': optimizer_runs,
    'constructorArguements': constructor_arguments,
    'evmversion': evm_version,
    'licenseType': license_number,
}

if chain in ['mainnet', 'ethlive']:
    chain_separator = False
    chain_id = ''
else:
    chain_separator = True
    chain_id = chain

url = 'https://api{0}{1}.etherscan.io/api'.format(
    '-' if chain_separator else '',
    chain_id
)

headers = {
    'User-Agent': ''
}

print('Sending verification request...')

verify = requests.post(url, headers = headers, data = data)

log(verify.request)

try:
    verify_response = json.loads(verify.text)
except json.decoder.JSONDecodeError:
    print(verify.text)
    exit('Error: Etherscan responded with invalid JSON.')

if verify_response['status'] != '1' or verify_response['message'] != 'OK':
    print('Error: ' + verify_response['result'])
    exit()

print('Sent verification request with guid ' + verify_response['result'])

guid = verify_response['result']

check_response = {}

while check_response == {} or 'pending' in check_response['result'].lower():

    if check_response != {}:
        print('Verification pending...')
        time.sleep(1)

    check = requests.post(url, headers = headers, data = {
        'apikey': api_key,
        'module': module,
        'action': 'checkverifystatus',
        'guid': guid,
    })

    if check_response == {}:
        log(check.request)

    try:
        check_response = json.loads(check.text)
    except json.decoder.JSONDecodeError:
        print(check.text)
        exit('Error: Etherscan responded with invalid JSON')

if check_response['status'] != '1' or check_response['message'] != 'OK':
    print('Error: ' + check_response['result'])
    exit()

print('Contract verified at https://{0}{1}etherscan.io/address/{2}#code'.format(
    chain_id,
    '.' if chain_separator else '',
    contract_address
))
