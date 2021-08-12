all     :; DAPP_LIBRARIES=' src/Math.sol:Math:0x0ed1C8a181F6012c4c1757F03Fa35a83B7a8FBd5' \
           DAPP_BUILD_OPTIMIZE=1 \
	   DAPP_BUILD_OPTIMIZE_RUNS=1 \
           dapp --use solc:0.6.12 build
