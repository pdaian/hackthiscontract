import easyweb3
import icontract
from eth_abi import encode_single, encode_abi
from web3 import Web3
import time


class Contract(icontract.IContract):
    def setup(self, web3_contract):
        # SourceTrixAreFor1337(uint _commitPhaseLengthInSeconds, string memory _choice1, string memory _choice2)
        #constructorParamsAbi = encode_abi(['uint256','string','string'],[60, "Alice", "Bob"])
        self.web3.transact_contract_method(web3_contract, self.contract_address, "SourceTrixAreFor1337", 0, (60, "Alice", "Bob"), 300)
        # commitVote(bytes32 _voteCommit)
        aliceVoteText = "1Alice"
        aliceVoteCommit = bytes(Web3.sha3(text=aliceVoteText))
        #aliceVoteAbi = encode_single('bytes32',aliceVoteCommit)
        self.web3.transact_contract_method(web3_contract, self.contract_address, "commitVote", 0, (aliceVoteCommit,), 300)
        time.sleep(60)
        # revealVote(string memory _vote, bytes32 _voteCommit)
        #revealAbi = encode_abi(['string','bytes32'], [aliceVoteText, aliceVoteCommit])
        self.web3.transact_contract_method(web3_contract, self.contract_address, "revealVote", 0, (aliceVoteText, aliceVoteCommit), 300)


    def has_been_hacked(self):
        #getWinner() public returns(string memory)
        winrar = self.web3.transact_contract_method(web3_contract, self.contract_address, "getWinner", 0, None, 300)
        if str(winrar) == "Bob":
            return True
        else:
            print("Winner is not Bob, winner is {}".format(winrar))
            return False
