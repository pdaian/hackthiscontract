import json
import subprocess
import threading
import time

import web3

import config as constants
import util
from web3.middleware import geth_poa_middleware


def new_web3():
    '''Return new IPC-based web3 instance'''
    return web3.Web3(web3.IPCProvider(constants.GETH_DATADIR + '/geth.ipc'))


class EasyWeb3:
    def __init__(self):
        self._web3 = new_web3()
        self._web3.middleware_stack.inject(geth_poa_middleware, layer=0)
        self._web3.eth.defaultAccount = constants.DEPLOY_FROM_ADDRESS
        self._web3.personal.unlockAccount(constants.DEPLOY_FROM_ADDRESS, "")
        self._lock = threading.Lock()
        self._status = None
        self._deployed_address = None

    def unlock_default_account(self):
        self._web3.personal.unlockAccount(constants.DEPLOY_FROM_ADDRESS, "")

    def compile_solidity(self, code):
        '''Compiles the given solidity code to EVM byte code.
        
        Returns a tuple (bytecode, abi), where bytecode is a hexstring
        and abi is a deserialized json object.
        '''
        input = {
            'language': 'Solidity',
            'sources': {
                'contract.sol': {
                    'content': code
                }
            },
            'settings': {
                'optimizer': {
                    'enabled': True,
                    'runs': 500
                },
                'outputSelection': {
                    'contract.sol': {
                        '*': ['abi', 'evm.bytecode']
                    }
                }
            }
        }

        solc = subprocess.Popen(
            [constants.SOLC4_PATH, '--standard-json'],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE)
        (out_json, err) = solc.communicate(input=json.dumps(input).encode('utf-8'))
        if solc.returncode != 0:
            raise Exception('solc crashed. returncode: {} errormsg: {}'.format(
                solc.returncode, err))
        out = json.loads(out_json.decode('utf-8'))
        for error in out.get('errors', []):
            if error['severity'] == 'error':
                raise Exception('solc compilation failed: {}'.format(error['message']))
        contracts = out['contracts']['contract.sol']
        if len(contracts) == 0:
            raise Exception('solc output contains no contract')
        if len(contracts) > 1:
            raise Exception('solc compiled multiple contracts. Which one is the right one?')
        contract = contracts[list(contracts.keys())[0]]
        return contract['evm']['bytecode']['object'], contract['abi']

    def deploy_named_solidity_contract(self, name, user_address, timeout=90):
        def wrapper():
            #    try:
            self._deploy_named_solidity_contract(name, user_address, timeout=timeout)

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

    def _deploy_named_solidity_contract(self, name, user_address, timeout=90):
        with open('{}/{}.json'.format(constants.CHALLENGE_DIR, name), 'r') as fd:
            config = json.load(fd)
        with open('{}/{}.sol'.format(constants.CHALLENGE_DIR, name), 'r') as fd:
            return self._deploy_solidity_contract(
                fd.read(), name, user_address,
                timeout=timeout)

    def deploy_status(self):
        with self._lock:
            return self._status, self._deployed_address

    def _deploy_solidity_contract(self, code, contract_name, user_address, timeout=180):
        '''Deploys the solidity contract given by code. 
        timeout is in seconds and specifies how long to 
        keep polling in the worst case.
        '''
        with self._lock:
            self._status = "compiling"
        web3 = self._web3
        bytecode, abi = self.compile_solidity(code)
        with self._lock:
            self._status = "compiled and processing"
        contract = web3.eth.contract(abi=abi, bytecode=bytecode)
        contract_address = None
        tx_hash = contract.constructor().transact()
        tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash, timeout)
        contract_address = tx_receipt.contractAddress

        with self._lock:
            self._status = "mined on-chain, post-processing"
            self._deployed_address = contract_address

        if (util.contract_exists(contract_name)):
            contract_helper = util.get_contract(user_address, contract_name, contract_address=contract_address)
            contract_helper.setup(contract)

        with self._lock:
            self._status = "deployed"
        return contract_address

    def balance(self, address):
        '''Returns the balance of address.'''
        return self._web3.eth.getBalance(address)

    def transact_contract_method(self, contract, contract_address, method_name, amount, timeout=180):
        '''Call a method of a contract through the "EasyWeb3" class, sending money as well'''
        tx_receipt = getattr(contract.transact({
            'from': self._web3.eth.defaultAccount,
            'to': contract_address,
            'value': int(amount)
        }), method_name)()
        t0 = time.time()
        while time.time() - t0 < timeout:
            if self._web3.eth.getTransactionReceipt(tx_receipt):
                break
            time.sleep(0.2)
        else:
            raise Exception("Deployment action timed out: {}".format(method_name))

    def call_contract_method(self, contract, contract_address, method_name, timeout=180):
        '''Call a method of a contract through the "EasyWeb3" class without sending any money to the contract'''
        tx_hash = getattr(contract.call({
            'from': self._web3.eth.defaultAccount,
            'to': contract_address,
            'value': int(amount)
        }), method_name)()
        try:
            tx_receipt = web3.eth.waitForTransactionReceipt(tx_hash, timeout)
        except Exception as e:
            raise Exception("Deployment action timed out: {}".format(method_name))
        return tx_receipt

if __name__ == '__main__':
    eweb3 = EasyWeb3()
    eweb3.unlock_default_account()
    a = eweb3.deploy_named_solidity_contract('03_ERC20', "0xEAf21008167fb3cC43a82B6197C273a7424322C8")
    #print(a)
    #print(eweb3.balance(str(a)))
    #print(eweb3.balance(new_web3().eth.coinbase))
