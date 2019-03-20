import easyweb3
import icontract
from eth_abi import encode_single, encode_abi
import time
import config as constants


class Contract(icontract.IContract):
    def setup(self):
        # assignplayers(address p1, address p2)
        assignplayers_tx_hash = self.contract_object.functions.assignplayers(self.user_address, constants.DEPLOY_FROM_ADDRESS).transact({"value": 0, "gas": 200000})
        self.eweb3._web3.eth.waitForTransactionReceipt(assignplayers_tx_hash)

        # deposit()
        deposit_tx_hash = self.contract_object.functions.deposit().transact({"value": 1000000000000000, "gas": 200000})
        self.eweb3._web3.eth.waitForTransactionReceipt(deposit_tx_hash)

    def has_been_hacked(self):
        winrar = self.contract_object.functions.winner().call()
        print("02_has_been_hacked winner is: {}".format(winrar))
        if winrar:
            if winrar != constants.DEPLOY_FROM_ADDRESS:
                return True
        return False
