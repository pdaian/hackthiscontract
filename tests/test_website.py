import os
import shutil
import unittest
import sys

sys.path.insert(0, os.path.abspath('..'))
import config as constants
import run
import util


class HackThisContractTest(unittest.TestCase):
    def setUp(self):
        self.app = run.app.test_client()
        self.MOCK_USER = "0x0000000000000000000000000000000000000008"
        self.MOCK_CHALLENGE = "404_TEST_CHALLENGE"
        self.MOCK_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000018"
        self.INVALID_ADDRESSES = ["0", "0x0", "0x000000000000000000000000000000000000001",
                                  "0x000000000000000000000000000000000000001G",
                                  "Hellö"]
        self.VALID_ADDRESSES = ["0x0000000000000000000000000000000000000008",
                                "0x31b98d14007bdee637298086988a0bbd31184523",
                                "0xb279182d99e65703f0076e4812653aab85fca0f0"]
        self.VALID_CHALLENGE = "03_ERC20"

    def tearDown(self):
        pass

    def test_index_loads(self):
        result = self.app.get("/")
        assert result.data is not None

    def test_ranking_loads(self):
        result = self.app.get("/ranking")
        assert result.data is not None

    def test_user_is_created(self):
        # Setup
        if os.path.exists(constants.DB_PATH + self.MOCK_USER):
            shutil.rmtree(constants.DB_PATH + self.MOCK_USER)

        # Validate
        assert not util.exists(self.MOCK_USER)
        assert util.exists(self.MOCK_USER)

        # Cleanup
        if os.path.exists(constants.DB_PATH + self.MOCK_USER):
            shutil.rmtree(constants.DB_PATH + self.MOCK_USER)

    def test_mark_finished(self):
        # Setup
        path = constants.DB_PATH + self.MOCK_USER + "/" + self.MOCK_CHALLENGE + '.done'
        if os.path.exists(path):
            os.remove(path)
        util.exists(self.MOCK_USER)

        # Validate
        assert not os.path.exists(path)
        util.mark_finished(self.MOCK_USER, self.MOCK_CHALLENGE)
        assert os.path.exists(path)

        # Cleanup
        if os.path.exists(path):
            os.remove(path)

    def test_write_address(self):
        # Setup
        path = constants.DB_PATH + self.MOCK_USER + "/" + self.MOCK_CHALLENGE
        if os.path.exists(path):
            os.remove(path)

        # Validate
        assert not os.path.exists(path)
        util.write_address(self.MOCK_USER, self.MOCK_CHALLENGE, self.MOCK_CONTRACT_ADDRESS)
        assert os.path.exists(path)
        with open(path) as fd:
            assert fd.read().strip() == self.MOCK_CONTRACT_ADDRESS

        # Cleanup
        if os.path.exists(path):
            os.remove(path)

    def test_is_valid_address(self):
        for a in self.VALID_ADDRESSES:
            assert util.is_valid_address(a)

        for a in self.INVALID_ADDRESSES:
            assert not util.is_valid_address(a)

    def test_util_get_status(self):
        # Setup
        path = constants.DB_PATH + self.MOCK_USER + "/" + self.MOCK_CHALLENGE
        if os.path.exists(path):
            os.remove(path)

        # Validate
        assert util.get_status(self.MOCK_USER, self.MOCK_CHALLENGE)[0] == "Not Started"
        util.write_address(self.MOCK_USER, self.MOCK_CHALLENGE, self.MOCK_CONTRACT_ADDRESS)
        assert util.get_status(self.MOCK_USER, self.MOCK_CHALLENGE)[0] == "Deployed / Unfinished"
        util.mark_finished(self.MOCK_USER, self.MOCK_CHALLENGE)
        assert util.get_status(self.MOCK_USER, self.MOCK_CHALLENGE)[0] == "Done!"

        # Cleanup
        if os.path.exists(path):
            os.remove(path)

    def test_contract_exists(self):
        assert not util.contract_exists(self.MOCK_CHALLENGE)
        assert util.contract_exists(self.VALID_CHALLENGE)

    def test_get_contract(self):
        # Setup
        contract_helper = util.get_icontract(self.MOCK_USER, self.VALID_CHALLENGE,
                                            contract_address=self.MOCK_CONTRACT_ADDRESS)

        # Validate
        assert contract_helper is not None
        assert contract_helper.contract_address == self.MOCK_CONTRACT_ADDRESS
        assert contract_helper.user_address == self.MOCK_USER
        assert contract_helper.web3 is not None

        # Cleanup
        shutil.rmtree(constants.DB_PATH + self.MOCK_USER)

    def test_get_contract_with_write_address(self):
        # Setup
        util.write_address(self.MOCK_USER, self.VALID_CHALLENGE, self.MOCK_CONTRACT_ADDRESS)
        contract_helper = util.get_icontract(self.MOCK_USER, self.VALID_CHALLENGE)

        # Validate
        assert contract_helper is not None
        assert contract_helper.contract_address == self.MOCK_CONTRACT_ADDRESS
        assert contract_helper.user_address == self.MOCK_USER
        assert contract_helper.web3 is not None

        # Cleanup
        shutil.rmtree(constants.DB_PATH + self.MOCK_USER)


if __name__ == '__main__':
    unittest.main()
