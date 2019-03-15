import threading
import time

import web3
from web3.middleware import geth_poa_middleware

import config as constants
import util

from flask import copy_current_request_context

def new_web3():
    """Return new IPC-based web3 instance"""
    return web3.Web3(web3.IPCProvider(constants.GETH_DATADIR + '/geth.ipc'))

class EasyWeb3:
    def __init__(self):
        """
        Initialise member values
        """
        self._web3 = new_web3()
        self._web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self._web3.eth.defaultAccount = constants.DEPLOY_FROM_ADDRESS
        self._web3.personal.unlockAccount(constants.DEPLOY_FROM_ADDRESS, "")
        self._lock = threading.Lock()
        self._status = None
        self._deployed_address = None

    def unlock_default_account(self):
        """
        Unlock the default account so that the server can sign and send transactions
        """
        self._web3.personal.unlockAccount(constants.DEPLOY_FROM_ADDRESS, "")

    def deploy_status(self):
        """
        Return deploy status of the given contract that this EasyWeb3 instance is connected to.
        :return: status, deployed_address - the status and address (if the status is deployed)
        """
        with self._lock:
            return self._status, self._deployed_address

    def grade_status(self):
        """
        Return grade status of the given contract /challenge tuple that this this EasyWeb3 instance
        is responsible for
        :return: status, deployed_address - the status and address
        """
        with self._lock:
            return self._status, self._deployed_address

    def deploy_named_solidity_contract(self, name, user_address, timeout=90):
        """
        Deploys a contract - spins off a thread to deploy the contract
        :param name: The challenge/contract name
        :param user_address: the address of the end-user that asked for this challenge
        :param timeout: how long to wait for things to happen on-chain - in seconds.
        """

        @copy_current_request_context
        def wrapper():
            #    try:
            self._deploy_solidity_contract(name, user_address, timeout=timeout)

        #    except Exception as ex:
        #        print 'Exception in ethereum.py'
        #        print ex
        #        import traceback
        #        traceback.print_exc()
        #        with self._lock:
        #            self._status = 'EXCEPTION: {}'.format(ex)
        t = threading.Thread(
            target=wrapper,
            args=()
        )
        t.start()

    def _deploy_solidity_contract(self, contract_name, user_address, timeout=180):
        """
        Deploys solidity contract
        :param contract_name: name of the challenge / the contract we're going to deploy
        :param user_address:  end-user address that asked for this challenge
        :param timeout: how long to wait for things to happen on-chain - in seconds
        :return: contract_address - address of this newly spawned contract
        """
        bytecode, abi = util.get_bytecode_abi(contract_name)
        with self._lock:
            self._status = "compiled and processing"
        contract = self._web3.eth.contract(abi=abi, bytecode=bytecode)
        contract_address = None
        tx_hash = contract.constructor().transact({'from': constants.DEPLOY_FROM_ADDRESS, 'gas': 2000000})
        tx_receipt = self._web3.eth.waitForTransactionReceipt(tx_hash, timeout)
        contract_address = tx_receipt.contractAddress

        with self._lock:
            self._status = "mined on-chain, post-processing"
            self._deployed_address = contract_address

        if (util.contract_exists(contract_name)):
            contract_helper = util.get_icontract(user_address, contract_name, contract_address=contract_address)
            contract_helper.setup()

        with self._lock:
            self._status = "deployed"

        return contract_address

    def grade_challenge(self, contract_name, user_address, timeout=90):
        """
        grades a challenge - spins off a thread to grade a challenge for a user
        :param name: The challenge/contract name
        :param user_address: the address of the end-user that asked for this challenge
        :param timeout: how long to wait for things to happen on-chain - in seconds.
        """
        def wrapper():
            self._grade_challenge(contract_name, user_address, timeout=timeout)

        t = threading.Thread(
            target=wrapper,
            args=()
        )
        t.start()

    def _grade_challenge(self, contract_name, user_address, timeout=180):
        """
        Deploys solidity contract
        :param contract_name: name of the challenge / the contract we're going to deploy
        :param user_address:  end-user address that asked for this challenge
        :param timeout: how long to wait for things to happen on-chain - in seconds
        :return: contract_address - address of this newly spawned contract
        """
        with self._lock:
            self._status = "started"
        contract_number = util.get_contract_number(contract_name)
        contract_addr = util.get_deployed_contract_address_for_challenge(user_address, contract_number)
        with self._lock:
            self._status = "in-progress"
            self._deployed_address = contract_address
        util.mark_grading(user_address, contract_number)

        if (util.contract_exists(contract_name)):
            contract_helper = util.get_icontract(user_address, contract_name, contract_address=contract_address)
            hacked = contract_helper.has_been_hacked()
            if hacked:
                util.mark_finished(user_address, contract_number)
            else:
                util.mark_in_progress(user_address, contract_number)

        with self._lock:
            self._status = "graded"

        return contract_address


    def balance(self, address):
        """
        Helper function - Returns the balance of an address.
        :param address: address to get the balance of
        :return: the balance of an address, in Wei
        """
        return self._web3.eth.getBalance(address)

    def transact_contract_method(self, contract, contract_address, method_name, amount, data=None, timeout=180):
        """
        Call a method of a contract through the "EasyWeb3" class, sending money as well
        :param contract: contract object/handler which is having the function called on it
        :param contract_address: address of this contract on chain
        :param method_name: name of the method to call
        :param amount: amount of money to send along with the function call. 0 is also acceptable.
        :param data: a python tuple of the function arguments of the method
        :param timeout: how long to wait for things to happen on chain, in seconds
        :return: ret_reciept - the TransactionReciept from web3 that has the return value of the contract method call
        """
        if data:
            tx_receipt = getattr(contract.transact({
                'from': self._web3.eth.defaultAccount,
                'to': contract_address,
                'value': int(amount),
                'gas': 200000
            }), method_name)(*data)
        else:
            tx_receipt = getattr(contract.transact({
                'from': self._web3.eth.defaultAccount,
                'to': contract_address,
                'value': int(amount),
                'gas': 200000
            }), method_name)()
        t0 = time.time()
        while time.time() - t0 < timeout:
            ret_reciept = self._web3.eth.getTransactionReceipt(tx_receipt)
            if ret_reciept:
                break
            time.sleep(0.2)
        else:
            raise Exception("Deployment action timed out: {}".format(method_name))
        return ret_reciept

