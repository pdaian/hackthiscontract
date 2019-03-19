pragma solidity^0.5.1;

contract CoinFlip {
    address public owner;
    address public player1;
    address public player2;
    mapping(address => bool) public deposited;
    mapping(address => uint256) public deposits;
    mapping(address => bool) public extended;
    uint256 public gamestart;
    uint256 public gameend;
    uint256 public mintoextend;
    uint256 public captoadd;
    uint256 public balance;
    bool public gameover;
    address public winner;

    constructor() public {
        mintoextend = 0.005 ether;
        captoadd = 0.01 ether;
        gameover = false;
        owner = msg.sender;
    }

    function assignplayers(address p1, address p2) public {
        require(msg.sender == owner);
        player1 = p1;
        player2 = p2;
    }

    function starthash() public view returns (bytes32 h) {
        return blockhash(gamestart);
    }

    function endhash() public view returns (bytes32 h) {
        return blockhash(gameend);
    }

    function deposit() public payable {
        require(!gameover);
        require(msg.sender == player1 || msg.sender == player2);
        require(!deposited[player1] || !deposited[player2]);
        deposits[msg.sender] = msg.value;
        deposited[msg.sender] = true;
        balance += msg.value;
        if (deposited[player1] && deposited[player2]) {
            gamestart = block.number;
            gameend = block.number + 20;
        }
    }

    /* Players can only extend the game with a monetary deposit
        to prevent arbitrary game extending (DoS). */
    function extend() public payable {
        require(!gameover);
        require(msg.sender == player1 || msg.sender == player2);
        require(!extended[player1] || !extended[player2] );
        if (msg.value > mintoextend) {
            /* Extend by 5 blocks */
            gameend = block.number + 5;
            if (msg.value > captoadd) {
                /* Refund money above the deposit cap */
                balance += (captoadd - mintoextend);
                msg.sender.call.value(msg.value - captoadd)("");
            } else {
                balance += msg.value;
            }
        }
        extended[msg.sender] = true;
    }

    /* Calculate the winner of the coin flip and
        reward them with the balance of the contract */
    function resolve() public {
        require(!gameover);
        require(block.number > gameend);
        gameover = true;
        uint256 win = ((uint256)(blockhash(gamestart) ^ blockhash(gameend))) % 10;
        if (win == 1) {
            winner = player1;
            player1.call.value(balance)("");
        } else {
            winner = player2;
            player2.call.value(balance)("");
        }
    }

}

