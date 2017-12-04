import ethereum
import validator


class ValidatorImpl(validator.Validator):
    def has_been_hacked(self):
        contract_bal = ethereum.EasyWeb3().balance(self.contract_address)
        if int(contract_bal) < 50000000000000000:
            return True
        else:
            return False
