import importlib.machinery
import importlib.util
import os
import types
from functools import wraps

from flask import render_template
import web3

import config as constants
import ethereum


def exists(user):
    if not os.path.exists(constants.DB_PATH):
        os.mkdir(constants.DB_PATH)
    if os.path.isdir(constants.DB_PATH + user):
        return True
    os.mkdir(constants.DB_PATH + user)
    return False


def get_status(user, challenge):
    if not os.path.isdir(constants.DB_PATH + user):
        return ("Not Started", "red")
    if not os.path.isfile(constants.DB_PATH + user + "/" + challenge):
        return ("Not Started", "red")
    with open(constants.DB_PATH + user + "/" + challenge) as fd:
        deployed_addr = fd.read().strip()
    if len(deployed_addr) == 0:
        return ("Error (redeploy)", "red")
    if os.path.isfile(constants.DB_PATH + user + "/" + challenge + ".done"):
        return ("Done!", "green", deployed_addr)
    return ("Deployed / Unfinished", "black", deployed_addr)


def write_address(user, challenge, address):
    if not os.path.exists(constants.DB_PATH):
        os.mkdir(constants.DB_PATH)
    if not os.path.exists(constants.DB_PATH + user):
        os.mkdir(constants.DB_PATH + user)

    with open(constants.DB_PATH + user + "/" + challenge, 'w') as fd:
        fd.write(address)


def mark_finished(user, challenge):
    with open(constants.DB_PATH + user + "/" + challenge + '.done', 'w') as fd:
        fd.write("")


def is_valid_address(address):
    web3_handle = ethereum.EasyWeb3()
    return web3_handle._web3.isAddress(address)


def check_address_decorator(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        # Because the address is sometimes in args and sometimes in kwargs
        address = None
        if 'address' in kwargs:
            address = kwargs['address']
        else:
            address = args[0]
        if not is_valid_address(address):
            return render_template("error.html")
        return fn(*args, **kwargs)

    return wrapped


def contract_exists(contract_name):
    file_name = constants.CHALLENGE_DIR + contract_name + ".py"

    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        print("Challenge validator not found for contract: " + contract_name)
        return False
    else:
        return True


def get_contract(address, contract_name, contract_address=None):
    if contract_address is None:
        contract_address = get_status(address, contract_name)[2].strip()

    if not contract_exists(contract_name):
        raise FileNotFoundError("challenges/" + contract_name + ".py")

    file_name = constants.CHALLENGE_DIR + contract_name + ".py"

    # Load the file
    loader = importlib.machinery.SourceFileLoader("contract", file_name)
    module = types.ModuleType(loader.name)

    loader.exec_module(module)

    # Setup
    contract = module.Contract()
    contract.contract_address = contract_address
    contract.user_address = address
    contract.web3 = ethereum.EasyWeb3()
    return contract
