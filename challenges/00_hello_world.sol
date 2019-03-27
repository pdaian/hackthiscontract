pragma solidity^0.5.0;

contract HelloWorldContract {
    address owner;
    bytes32 public ownerflag;
    bytes32 public userflag;

    event HelloWorld(string, bytes32);

    constructor() public {
        owner = msg.sender;
    }

    function setOwnerFlag(bytes32 _ownerflag) public {
        if (msg.sender == owner) ownerflag = _ownerflag;
    }

    function helloworld(string memory _yourstring, bytes32 _yourflag) public {
        emit HelloWorld(_yourstring, _yourflag);
        userflag = _yourflag;
    }
}
