import easyweb3
import icontract
from eth_abi import encode_single, encode_abi
import time
import config as constants
import util

DEPOSIT_AMT = 5000000000000000
class Contract(icontract.IContract):
    def setup(self):
        contract_name = "06_wallet_library"
        bytecode, abi = util.get_bytecode_abi(contract_name)
        wallet_library_contract = self.eweb3._web3.eth.contract(abi=abi, bytecode=bytecode)
        wallet_library_contract_address = None

        # deploy wallet library contract
        tx_hash = wallet_library_contract.constructor().transact({'from': constants.DEPLOY_FROM_ADDRESS, 'gas': 2000000})
        tx_receipt = self.eweb3._web3.eth.waitForTransactionReceipt(tx_hash)
        wallet_library_contract_address = tx_receipt.contractAddress

        # set wallet library's address in the wallet contract
        # to the wallet library deployed above
        wallet_library_tx_hash = self.contract_object.functions.setWalletLibrary(wallet_library_contract_address).transact({
            "from": constants.DEPLOY_FROM_ADDRESS,
            "value": 0,
            "gas": 200000})
        wallet_library_tx_receipt = self.eweb3._web3.eth.waitForTransactionReceipt(wallet_library_tx_hash)

        # deposit ether in the wallet contract
        deposit_tx_hash = self.eweb3._web3.eth.sendTransaction({
            "from":    constants.DEPLOY_FROM_ADDRESS,
            "to": self.contract_object.address,
            "value": DEPOSIT_AMT,
            "gas": 500000})
        deposit_tx_receipt = self.eweb3._web3.eth.waitForTransactionReceipt(deposit_tx_hash)

    def has_been_hacked(self):
        contract_bal = self.eweb3._web3.eth.getBalance(self.contract_object.address)
        print(contract_bal)
        if contract_bal < DEPOSIT_AMT:
            return True
        else:
            return False
