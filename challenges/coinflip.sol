pragma solidity^0.4.0;

contract CoinFlip {
    
    address public player1;
    address public player2;
    mapping(address => bool) deposited;
    mapping(address => uint256) deposits;
    mapping(address => bool) extended;
    uint256 public gamestart;
    uint256 public gameend;
    uint256 mintoextend;
    uint256 captoadd;
    uint256 balance;
    bool gameover;
    
    function CoinFlip(address p1, address p2) {
        player1 = p1;
        player2 = p2;
        mintoextend = 0.005 ether;
        captoadd = 0.01 ether;
        gameover = false;
    }
    
    function starthash() constant returns (bytes32 h) {
        return block.blockhash(gamestart);
    }
    
    function endhash() constant returns (bytes32 h) {
        return block.blockhash(gameend);
    }
    
    function deposit() payable {
        require(!gameover);
        require(msg.sender == player1 || msg.sender == player2);
        require(!deposited[player1] || !deposited[player2]);
        deposits[msg.sender] = msg.value;
        deposited[msg.sender] = true;
        balance += msg.value;
        if (deposited[player1] && deposited[player2]) {
            gamestart = block.number;
            gameend = block.number + 100;
        }
    }
    
    /* Players can only extend the game with a monetary deposit
        to prevent arbitrary game extending (DoS). */
    function extend() payable {
        require(!gameover);
        require(msg.sender == player1 || msg.sender == player2);
        require(!extended[player1] || !extended[player2] );
        if (msg.value > mintoextend) {
            /* Extend by 50 blocks */
            gameend += 50;
            if (msg.value > captoadd) {
                /* Refund money above the deposit cap */
                balance += (captoadd - mintoextend);
                msg.sender.call.value(msg.value - captoadd)();
            } else {
                balance += msg.value;
            }
        }
        extended[msg.sender] = true;
    }
    
    /* Calculate the winner of the coin flip and 
        reward them with the balance of the contract */
    function resolve() {
        require(!gameover);
        require(block.number > gameend);
        gameover = true;
        uint256 winner = ((uint256)(block.blockhash(gamestart) ^ block.blockhash(gameend))) % 2;
        if (winner == 1) {
            player1.call.value(balance)();
        } else {
            player2.call.value(balance)();
        }
    }
    
}
