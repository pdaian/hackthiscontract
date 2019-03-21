import easyweb3
import icontract


class Contract(icontract.IContract):
    def setup(self):
        # deposit()
        initial_deposit_tx_hash = self.contract_object.functions.deposit().transact({"value": 5000000000000000, "gas": 200000})
        self.eweb3._web3.eth.waitForTransactionReceipt(initial_deposit_tx_hash)

    def has_been_hacked(self):
        contract_bal = self.eweb3._web3.eth.getBalance(self.contract_address)
        if int(contract_bal) < 5000000000000000:
            return True
        else:
            return False
