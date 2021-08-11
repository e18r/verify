// SPDX-License-Identifier: AGPL-3.0-or-later

pragma solidity 0.8.6;

import "./Math.sol";

contract c {
    function f() public pure returns (uint256) {
        return Math.pi();
    }
    function g() public pure returns (bool) {
        return true;
    }
}
