#! /bin/env python3

import os, sys, subprocess, json, requests

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

flatten = subprocess.run(['hevm', 'flatten', '--source-file', contract_path], capture_output=True)

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
    'licenseType': license_number
}

print(data)

seth_chain = subprocess.run(['seth', 'chain'], capture_output=True)
chain = seth_chain.stdout.decode('ascii').replace('\n', '')

if chain in ['mainnet', 'ethlive']:
    chain_chunk = ''
else:
    chain_chunk = '-' + chain

url = 'https://api{}.etherscan.io/api'.format(chain_chunk)

headers = {
    'User-Agent': ''
}

r = requests.post(url, headers = headers, data = data)

print(r.request.url)
print(r.request.method)
print(r.request.headers)
print(r.request.body)

try:
    response = json.loads(r.text)
except json.decoder.JSONDecodeError:
    print(r.text)
    exit()

if response['status'] != '1' or response['message'] != 'NOTOK':
    print('Error: ' + response['result'])
    exit()

print('Success: ' + response['result'])
