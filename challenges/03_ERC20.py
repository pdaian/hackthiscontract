import easyweb3
import icontract


class Contract(icontract.IContract):
    def setup(self, web3_contract):
        self.web3.transact_contract_method(web3_contract, self.contract_address, "deposit", 50000000000000000)

    def has_been_hacked(self):
        contract_bal = easyweb3.EasyWeb3().balance(self.contract_address)
        if int(contract_bal) < 50000000000000000:
            return True
        else:
            return False
