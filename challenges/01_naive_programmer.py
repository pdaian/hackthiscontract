import easyweb3
import icontract
from eth_abi import encode_single, encode_abi
import time
import config as constants


class Contract(icontract.IContract):
    def setup(self):
        # SourceTrixAreFor1337(uint _commitPhaseLengthInSeconds, string memory _choice1, string memory _choice2)
        stafl_tx_hash = self.contract_object.functions.SourceTrixAreFor1337(25, "Alice", "Bob").transact({"value": 0, "gas": 200000})
        self.eweb3._web3.eth.waitForTransactionReceipt(stafl_tx_hash)

        # commitVote(bytes32 _voteCommit)
        aliceVoteText = "1Alice"
        aliceVoteCommit = bytes(self.eweb3._web3.sha3(text=aliceVoteText))
        commit_tx_hash = self.contract_object.functions.commitVote(aliceVoteCommit).transact({"value": 0, "gas": 200000})
        self.eweb3._web3.eth.waitForTransactionReceipt(commit_tx_hash)

        time.sleep(35)

        # revealVote(string memory _vote, bytes32 _voteCommit)
        reveal_tx_hash = self.contract_object.functions.revealVote(aliceVoteText, aliceVoteCommit).transact({"value": 0, "gas": 200000})
        self.eweb3._web3.eth.waitForTransactionReceipt(reveal_tx_hash)

    def has_been_hacked(self):
        # This is an empty transaction for testing
        force_next_block = self.eweb3._web3.eth.sendTransaction({"from":constants.DEPLOY_FROM_ADDRESS, "to": constants.DEPLOY_FROM_ADDRESS, "value":0})
        next_receipt = self.eweb3._web3.eth.waitForTransactionReceipt(force_next_block)

        # getWinner() public returns(string memory)
        winrar_tx_hash = self.contract_object.functions.getWinner().transact({"gas": 200000})
        winrar_tx_receipt = self.eweb3._web3.eth.waitForTransactionReceipt(winrar_tx_hash)
        winrar_logs = self.contract_object.events.voteWinner().processReceipt(winrar_tx_receipt)

        if winrar_logs:
            if len(winrar_logs) > 0:
                print(winrar_logs[0]['args'][''])
                if winrar_logs[0]['args'][''] == 'Bob':
                    return True
        return False
