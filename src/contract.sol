// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity 0.6.12;

import "./Math.sol";

contract c {
    function f() public pure returns (uint256) {
        return Math.pi();
    }
    function g() public pure returns (uint256) {
        return 45209387234;
    }
}
