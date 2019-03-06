import os
import unittest
import sys
import sqlite3

sys.path.insert(0, os.path.abspath('.'))
import config as constants
import util
import run
import easyweb3


prefundedAddr = None

class HackThisContractEasyWeb3Test(unittest.TestCase):
    def setUp(self):
        self.app = run.app.test_client()
        self.MOCK_USER = "0x0000000000000000000000000000000000000008"
        self.MOCK_CONTRACT_ADDRESS = "0x0000000000000000000000000000000000000018"
        self.VALID_ADDRESSES = ["0x0000000000000000000000000000000000000008",
                                "0x31b98d14007bdee637298086988a0bbd31184523",
                                "0xb279182d99e65703f0076e4812653aab85fca0f0"]
        with run.app.app_context():
            util.init_db()

    def tearDown(self):
        if os.path.isfile(constants.DB_PATH):
            os.remove(constants.DB_PATH)

    def test_contract_deployment(self):
        constants.GETH_DATADIR = "/tmp"
        constants.DEPLOY_FROM_ADDRESS = prefundedAddr
        w3handle = easyweb3.EasyWeb3()
        cbase = w3handle.balance(w3handle._web3.eth.defaultAccount)
        self.assertIsNotNone(cbase)
        cAddr = w3handle._deploy_solidity_contract("01_naive_programmer",w3handle._web3.eth.defaultAccount)
        self.assertIsNotNone(cAddr)



if __name__ == '__main__':
    prefundedAddr = input("What is your geth --dev default address with prefunded money for testing? ")
    unittest.main()
