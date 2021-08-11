#! /bin/bash

curl https://api-kovan.etherscan.io/api -d apikey=$ETHERSCAN_API_KEY -d module=contract -d action=checkverifystatus -d guid=$1

echo ""
