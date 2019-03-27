import os
import unittest
import sys
import sqlite3
import time

sys.path.insert(0, os.path.abspath('.'))
import config as constants
import util
import run
import easyweb3


prefundedAddr = None
FIVE_ETHER = 5000000000000000000

class HackThisContractChallengesTest(unittest.TestCase):
    def setUp(self):
        self.app = run.app.test_client()
        self.MOCK_USER = "0x2AA1710B555E6cc1Ac98c0eC48B51d61f3273949"
        self.MOCK_PRIVATE_KEY = "03075139118396fa0bf41e804f31eaf25740e305164fcd9d870652cc984e5d63" # NEVER USE THIS IN PROD ZOMG
        with run.app.app_context():
            util.init_db()

    def tearDown(self):
        pass
        if os.path.isfile(constants.DB_PATH):
            os.remove(constants.DB_PATH)

    def test_challenges_00_hello_world(self):
        w3handle = easyweb3.EasyWeb3()
        cbase = w3handle._web3.eth.getBalance(w3handle._web3.eth.defaultAccount)
        self.assertIsNotNone(cbase)
        # Fund user account so they have money too
        try:
            w3handle._web3.personal.importRawKey(self.MOCK_PRIVATE_KEY, "")
        except ValueError as accountAlreadyExists:
            print("skipping importing the key for the mock user twice")

        w3handle._web3.personal.unlockAccount(self.MOCK_USER, "")
        fund_tx = w3handle._web3.eth.sendTransaction({"from":prefundedAddr, "to":self.MOCK_USER, "value":FIVE_ETHER})
        w3handle._web3.eth.waitForTransactionReceipt(fund_tx)

        self.assertGreaterEqual(w3handle._web3.eth.getBalance(self.MOCK_USER), FIVE_ETHER)

        cAddr = w3handle._deploy_solidity_contract("00_hello_world", w3handle._web3.eth.defaultAccount)
        self.assertIsNotNone(cAddr)

        icontract = util.get_icontract(self.MOCK_USER, "00_hello_world", contract_address=cAddr)
        _, reconstructed_abi = util.get_bytecode_abi("00_hello_world")
        reconstructed_contract_handle = w3handle._web3.eth.contract(abi=reconstructed_abi, address=cAddr)

        self.assertFalse(icontract.has_been_hacked())

        # solve the challenge
        instring = self.MOCK_USER + "a very useless salt"
        solution_tx_hash = reconstructed_contract_handle.functions.helloworld(
                                "hello",
                                w3handle._web3.sha3(text=instring)
        ).transact({"from": self.MOCK_USER, "gas":500000})
        solution_tx_receipt = w3handle._web3.eth.waitForTransactionReceipt(solution_tx_hash)

        self.assertTrue(icontract.has_been_hacked())

    def test_challenges_01_naive_programmer(self):
        w3handle = easyweb3.EasyWeb3()
        cbase = w3handle._web3.eth.getBalance(w3handle._web3.eth.defaultAccount)
        self.assertIsNotNone(cbase)
        # Fund user account so they have money too
        try:
            w3handle._web3.personal.importRawKey(self.MOCK_PRIVATE_KEY, "")
        except ValueError as accountAlreadyExists:
            print("skipping importing the key for the mock user twice")

        w3handle._web3.personal.unlockAccount(self.MOCK_USER, "")
        fund_tx = w3handle._web3.eth.sendTransaction({"from":prefundedAddr, "to":self.MOCK_USER, "value":FIVE_ETHER})
        w3handle._web3.eth.waitForTransactionReceipt(fund_tx)

        self.assertGreaterEqual(w3handle._web3.eth.getBalance(self.MOCK_USER), FIVE_ETHER)

        cAddr = w3handle._deploy_solidity_contract("01_naive_programmer",w3handle._web3.eth.defaultAccount)
        self.assertIsNotNone(cAddr)

        icontract = util.get_icontract(self.MOCK_USER, "01_naive_programmer", contract_address=cAddr)
        _, reconstructed_abi = util.get_bytecode_abi("01_naive_programmer")
        reconstructed_contract_handle = w3handle._web3.eth.contract(abi=reconstructed_abi, address=cAddr)

        self.assertFalse(icontract.has_been_hacked())

        # solve the challenge

        solution_tx_hash = reconstructed_contract_handle.functions.SourceTrixAreFor1337(21, "Bob", "Alice").transact({"from": self.MOCK_USER, "gas":500000})
        solution_tx_receipt = w3handle._web3.eth.waitForTransactionReceipt(solution_tx_hash)

        time.sleep(30)

        self.assertTrue(icontract.has_been_hacked())

if __name__ == '__main__':
    prefundedAddr = input("What is your geth --dev default address with prefunded money for testing? ")
    constants.GETH_DATADIR = "/tmp"
    constants.DEPLOY_FROM_ADDRESS = prefundedAddr
    unittest.main()
