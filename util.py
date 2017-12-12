import importlib.machinery
import importlib.util
import os
import types
from functools import wraps

from flask import render_template
from web3.utils import validation

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
        os.mkdir(constants.DB_PATH)  # TODO: Is this working?

    print("write_address\t" + address)
    print("user:\t" + user)
    with open(constants.DB_PATH + user + "/" + challenge, 'w') as fd:
        fd.write(address)


def mark_finished(user, challenge):
    with open(constants.DB_PATH + user + "/" + challenge + '.done', 'w') as fd:
        fd.write("")


def is_valid_address(address):
    return validation.is_address(address)


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
    file_name = "challenges/" + contract_name + ".py"

    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        print("Challenge validator not found for contract: " + contract_name)
        return False
    else:
        return True


def get_contract(address, contract_name):
    if not contract_exists(contract_name):
        raise FileNotFoundError("challenges/" + contract_name + ".py")

    file_name = "challenges/" + contract_name + ".py"
    contract_addr = get_status(address, contract_name)[2].strip()

    # Load the file
    loader = importlib.machinery.SourceFileLoader("contract", file_name)
    module = types.ModuleType(loader.name)

    loader.exec_module(module)

    # Setup
    contract = module.Contract()
    contract.contract_address = contract_addr
    contract.user_address = address
    contract.web3 = ethereum.EasyWeb3()
    print("util" + str(dir(contract)))
    return contract


def get_contract_by_address(contract_address):
    result = [os.path.join(dp, f) for dp, dn, filenames in os.walk(constants.DB_PATH) for f in filenames if
              not os.path.splitext(f)[1] == '.done']

    for s in result:
        with open(s) as f:
            address = f.readline()
            if (address == contract_address):
                parts = s.split("/")
                return get_contract(parts[len(parts) - 2], parts[len(parts) - 1])
    raise EnvironmentError("Failed to find contract with address: " + contract_address)
