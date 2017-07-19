import json
import subprocess
import threading
import time

import web3

CHALLENGE_DIR = '/home/ubuntu/hackthiscontract/challenges'
GETH_DATADIR = '/home/ubuntu/geth_rinkeby'
SOLC_PATH = '/usr/bin/solc'

def newWeb3():
	'''Return new IPC-based web3 instance'''
	return web3.Web3(web3.IPCProvider(GETH_DATADIR + '/geth.ipc'))

class EasyWeb3:
	def __init__(self):
		self._web3 = newWeb3()
		self._lock = threading.Lock()
		self._status = None
		self._deployed_address = None

	def unlock_coinbase(self):
		'''Unlock coinbase account'''
		self._web3.personal.unlockAccount(self._web3.eth.coinbase, "")
	
	def compile_solidity(self, code):
		'''Compiles the given solidity code to EVM byte code.
		
		Returns a tuple (bytecode, abi), where bytecode is a hexstring
		and abi is a deserialized json object.
		'''
		input={
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
			[SOLC_PATH, '--standard-json'], 
			stdout=subprocess.PIPE, 
			stdin=subprocess.PIPE, 
			stderr=subprocess.PIPE)
		(out_json, err) = solc.communicate(input=json.dumps(input))
		if solc.returncode != 0:
			raise Exception('solc crashed. returncode: {} errormsg: {}'.format(
				solc.returncode, err))
		out = json.loads(out_json)
		for error in out.get('errors', []):
			if error['severity'] == 'error':
				raise Exception('solc compilation failed: {}'.format(error['message']))
		contracts = out['contracts']['contract.sol']
		if len(contracts) == 0:
			raise Exception('solc output contains no contract')
		if len(contracts) > 1:
			raise Exception('solc compiled multiple contracts. Which one is the right one?')
		contract = contracts[contracts.keys()[0]]	
		return contract['evm']['bytecode']['object'], contract['abi']

	def deploy_named_solidity_contract(self, name, timeout=90):
		def wrapper():
		#	try:
			self._deploy_named_solidity_contract(name, timeout=timeout)
		#	except Exception as ex:
		#		print 'Exception in ethereum.py'
		#		print ex
		#		import traceback
		#		traceback.print_exc()
		#		with self._lock:
		#			self._status = 'EXCEPTION: {}'.format(ex)
		t = threading.Thread(
			target=wrapper,
			args=()
		)
		t.start()

	
	def _deploy_named_solidity_contract(self, name, timeout=90):
		'''Like deploy_solidity_contract, but reads the contract
		file and deploy_actions for you.'''
		with open('{}/{}.json'.format(CHALLENGE_DIR, name), 'r') as fd:
			config = json.load(fd)	
		with open('{}/{}.sol'.format(CHALLENGE_DIR, name), 'r') as fd:
			return self._deploy_solidity_contract(
				fd.read(),
				deploy_actions=config.get('on_deploy', []), 
				timeout=timeout)
	

	def deploy_status(self):
		with self._lock:
			return self._status, self._deployed_address

	def _deploy_solidity_contract(self, code, deploy_actions=[], timeout=90):
		'''Deploys the solidity contract given by code. Uses nasty
		polling loop to give you the illusion of a synchronous call.
		timeout is
		in seconds and specifies how long to keep polling in the
		worst case.
		'''
		with self._lock:
			self._status = "compiling"
		web3 = self._web3
		bytecode, abi = self.compile_solidity(code)
		with self._lock:
			self._status = "compiled and processing"
		contract = web3.eth.contract(abi=abi, bytecode=bytecode)
		contract_address = None
		tx_receipt = contract.deploy()
		t0 = time.time()
		while time.time() - t0 < timeout:
			receipt = web3.eth.getTransactionReceipt(tx_receipt)
			if receipt:
				contract_address = receipt['contractAddress']
				break
			# nasty polling loop 
			time.sleep(0.2)
		else:
			raise Exception("Deployment timed out.")

		with self._lock:
			self._status = "mined on-chain, post-processing"
			self._deployed_address = contract_address

		for i, action in enumerate(deploy_actions):
			tx_receipt = getattr(contract.transact({
				'from': self._web3.eth.coinbase, 
				'to': contract_address,
				'value': action['value']
			}), action['method'])()
			while time.time() - t0 < timeout:
				if web3.eth.getTransactionReceipt(tx_receipt):
					break
				time.sleep(0.2)
			else:
				raise Exception("Deployment actions timed out.")
			with self._lock:
				self._status = "postprocessing deploy action {}/{}".format(i, len(deploy_actions))

		with self._lock:
			self._status = "deployed"

	def balance(self, address):
		'''Returns the balance of address.
		'''
		return self._web3.eth.getBalance(address)
		
	
if __name__ == '__main__':
	CODE = '''pragma solidity ^0.4.0;
contract SimpleStorage {
    uint storedData;

    function SimpleStorage() {
        storedData = 0x1337;
    }

    function set(uint x) {
        storedData = x;
    }

    function get() constant returns (uint) {
        return storedData;
    }
}'''
	eweb3 = EasyWeb3()
	eweb3.unlockCoinbase()
	a = eweb3.deploy_named_solidity_contract('ERC20')
	print a
	print eweb3.balance(a)
	print eweb3.balance(newWeb3().eth.coinbase)
