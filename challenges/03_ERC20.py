import ethereum
import validator


class ValidatorImpl(validator.Validator):
    def perform_validation(self):
        contract_bal = ethereum.EasyWeb3().balance(self.contract_address)
        if 50000000000000000 > int(contract_bal):
            self.set_hacked()
        else:
            self.set_not_hacked()
