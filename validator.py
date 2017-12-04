class Validator:
    def __init__(self):
        self.contract_address = None
        self.user_address = None

    '''Returns true if the contract has been hacked, false otherwise'''

    def has_been_hacked(self):
        raise NotImplementedError("perform_validation is not implemented!")
