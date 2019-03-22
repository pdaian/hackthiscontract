pragma solidity^0.5.0;

contract TestToken {
    string constant name = "Bad ICO Token";
    string constant symbol = "IC3";
    uint8 constant decimals = 18;
    uint public totaltokens;
    uint public totaleth;
    uint256 bonustime;
    uint256 bonuscap;

    struct Allowed {
        mapping (address => uint256) _allowed;
    }

    mapping (address => Allowed) allowed;
    mapping (address => uint256) balances;

    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

    modifier IsBelowBonusCap() {
        if (msg.value + totaltokens <= bonuscap) {
            _;
        }
    }

    constructor() public {
        totaltokens = 0;
        totaleth = 0;
        bonustime = now + 2 minutes;
        bonuscap = 3133700000000000;
    }

    function totalSupply() public view returns (uint256) {
        return totaltokens;
    }

    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
    }

    function depositwithbonus() public payable IsBelowBonusCap returns (bool) {
        if (balances[msg.sender] + msg.value < msg.value) return false;
        if (totaltokens + msg.value < msg.value) return false;
        if (msg.value + totaltokens > bonuscap) {
            /* Refund sender if bonus cap is exceeded. */
            msg.sender.send(msg.value);
            return false;
        }
        balances[msg.sender] += (msg.value + (msg.value/5));
        totaltokens += (msg.value + (msg.value/5));
        totaleth += msg.value;
        return true;
    }

    function deposit() public payable returns (bool success) {
        if (balances[msg.sender] + msg.value < msg.value) return false;
        if (totaltokens + msg.value < msg.value) return false;
        balances[msg.sender] += msg.value;
        totaltokens += msg.value;
        totaleth += msg.value;
        return true;
    }

    function withdraw(uint256 _value) public returns (bool success) {
        if (balances[msg.sender] < _value) return false;
        balances[msg.sender] -= _value;
        msg.sender.transfer(_value);
        totaltokens -= _value;
        totaleth -= _value;
        return true;
    }

    function transfer(address _to, uint256 _value) public returns (bool success) {
        if (balances[msg.sender] < _value) return false;

        if (balances[_to] + _value < _value) return false;
        balances[msg.sender] -= _value;
        balances[_to] += _value;

        emit Transfer(msg.sender, _to, _value);

        return true;
    }


    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowed[msg.sender]._allowed[_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function allowance(address _owner, address _spender) public view returns (uint256 remaining) {
        return allowed[_owner]._allowed[_spender];
    }

    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        if (balances[_from] < _value) return false;
        if ( allowed[_from]._allowed[msg.sender] < _value) return false;
        if (balances[_to] + _value < _value) return false;

        balances[_from] -= _value;
        balances[_to] += _value;
        allowed[_from]._allowed[msg.sender] -= _value;
        return true;
    }

}
