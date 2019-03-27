import easyweb3
import icontract
from eth_abi import encode_single, encode_abi
import time
import config as constants


class Contract(icontract.IContract):
    def setup(self):
        # setOwnerFlag(bytes32 _ownerflag)
        instr = self.user_address + "a very useless salt"
        ownerflag = bytes(self.eweb3._web3.sha3(text=instr))
        commit_tx_hash = self.contract_object.functions.setOwnerFlag(ownerflag).transact({"value": 0, "gas": 200000})
        self.eweb3._web3.eth.waitForTransactionReceipt(commit_tx_hash)

    def has_been_hacked(self):
        userflag = self.contract_object.functions.userflag().call()
        print(userflag.hex())
        instr = self.user_address + "a very useless salt"
        if userflag == bytes(self.eweb3._web3.sha3(text=instr)):
            return True
        return False
