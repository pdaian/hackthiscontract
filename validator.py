class Validator:
    def __init__(self):
        self.contract_address = None
        self.user_address = None

        self.hacked = None

    def perform_validation(self):
        raise NotImplementedError("perform_validation is not implemented!")

    def set_hacked(self):
        self.hacked = True

    def set_not_hacked(self):
        self.hacked = False

    def is_hacked(self):
        if self.hacked is None:
            return False
        else:
            return self.hacked

    def is_validating(self):
        if self.hacked is None:
            return True
