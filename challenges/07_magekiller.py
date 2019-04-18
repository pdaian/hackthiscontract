import easyweb3
import icontract
from eth_abi import encode_single, encode_abi
import time
import config as constants
import util

class Contract(icontract.IContract):
    def setup(self):
        bytecode, abi = util.get_bytecode_abi("07_wallet_library")
        wallet_library_contract = self.eweb3._web3.eth.contract(abi=abi, bytecode=bytecode)
        wallet_library_contract_address = None

        # deploy wallet library contract
        tx_hash = wallet_library_contract.constructor().transact({'from': constants.DEPLOY_FROM_ADDRESS, 'gas': 2000000})
        tx_receipt = self.eweb3._web3.eth.waitForTransactionReceipt(tx_hash, 180)
        wallet_library_contract_address = tx_receipt.contractAddress

        # set wallet library's address in the wallet contract
        # to the wallet library deployed above
        wallet_library_tx_hash = self.contract_object.functions.setWalletLibrary(wallet_library_contract_address).transact({
            "from": constants.DEPLOY_FROM_ADDRESS,
            "value": 0,
            "gas": 2000000})
        wallet_library_tx_receipt = self.eweb3._web3.eth.waitForTransactionReceipt(wallet_library_tx_hash, 180)

    def has_been_hacked(self):
        wallet_library_address = self.contract_object.functions._walletLibrary().call()
        bytecode = self.eweb3._web3.eth.getCode(wallet_library_address)
        if len(bytecode) == 0:
            return True
        else:
            return False


