import easyweb3
import icontract


class Contract(icontract.IContract):
    def setup(self):
        pass

    def has_been_hacked(self):
        contract_bal = self.eweb3._web3.eth.getBalance(self.contract_address)
        weth_bal = self.contract_object.functions.totaleth().call()
        if weth_bal != contract_bal:
            return True
        else:
            return False
