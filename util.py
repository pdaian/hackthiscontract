import importlib.machinery
import importlib.util
import os
import types
from functools import wraps

from flask import render_template, g
import web3

import config as constants
import easyweb3
import sqlite3

def init_db():
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS htctable(
        userid INTEGER PRIMARY KEY,
        useraddress TEXT NOT NULL UNIQUE,
        score INTEGER,
        c1state INTEGER,
        c1deployaddr TEXT,
        c2state INTEGER,
        c2deployaddr TEXT,
        c3state INTEGER,
        c3deployaddr TEXT,
        c4state INTEGER,
        c4deployaddr TEXT
    );"""
    htcdb = get_db()
    cur = htcdb.execute(create_table_sql)
    htcdb.commit()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(constants.DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), onlyFirstRow=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if onlyFirstRow else rv


def exists(user):
    """
    Check if a users information is stored in the HackThisContract database, and make them exist if they don't.
    :param user: user address to check against
    :return: whether or not the user is in our database
    """
    htcdb = get_db()
    status_query = "SELECT * FROM htctable WHERE useraddress = ?"
    qresp = query_db(status_query, (user, ), True)
    if qresp is None: # len(qresp) == 0: # user does not yet exist
        cur = htcdb.execute("""
        INSERT INTO htctable(
            useraddress,
            score,
            c1state,
            c2state,
            c3state,
            c4state
        ) VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        );
        """,
        (
            user,
            0,
            constants.STATE_NOT_STARTED,
            constants.STATE_NOT_STARTED,
            constants.STATE_NOT_STARTED,
            constants.STATE_NOT_STARTED
        ))
        htcdb.commit()
        return False

    return True



def write_address(user, challenge, address):
    """
    Writes a user's address into the HackThisContract database
    :param user: user address to write
    :param challenge: which challenge they're working on
    :param address: address of the deployed challenge contract for this user
    :return:
    """
    exists(user)
    deployed_addr_column_name = "c" + str(int(challenge)) + "deployaddr"
    state_column_name = "c" + str(int(challenge)) + "state"
    htcdb = get_db()
    cur = htcdb.execute("UPDATE htctable SET {0} = ?, {1} = ? WHERE useraddress = ?".format(deployed_addr_column_name, state_column_name),
                        (address, constants.STATE_DEPLOYED_IN_PROGRESS, user))
    htcdb.commit()


def mark_finished(user, challenge):
    """
    Mark a challenge as finished in the HackThisContract Database
    :param user: user address that completed the challenge
    :param challenge: which challenge
    :return:
    """
    exists(user)
    state_column_name = "c" + str(int(challenge)) + "state"
    htcdb = get_db()
    cur = htcdb.execute("UPDATE htctable SET {0} = ? WHERE useraddress = ?".format(state_column_name), (constants.STATE_FINISHED, user))
    htcdb.commit()

def get_contract_number(contract_name):
    """
    Simple helper function to return the number corresponding to a contract name
    :param contract_name the name of the contract you're working with
    :return number - the number for this contract in the db
    """
    return int(contract_name.split("_")[0])


def get_status(user, challenge_number):
    """
    Returns the completion status of a (user, challenge_number) tuple on our system
    :param user: the user address to check against
    :param challenge_number: which challenge to check against
    :return: statusTuple - status, color, deployed_contract_address
    """
    state_column_name = "c" + str(int(challenge_number)) + "state"
    deployed_addr_column_name = "c" + str(int(challenge_number)) + "deployaddr"
    status_query = "SELECT {}, {} FROM htctable WHERE useraddress = ?".format(state_column_name, deployed_addr_column_name)
    qresp = query_db(status_query, (user, ), True)
    if qresp is None:
        return ("Not Started/Error", "red")
    state = list(qresp)[0]
    deployed_addr = list(qresp)[1]
    if state == constants.STATE_NOT_STARTED:
        return ("Not Started", "red")
    elif state == constants.STATE_DEPLOYED_IN_PROGRESS:
        return ("Deployed / Unfinished", "black", deployed_addr)
    elif state == constants.STATE_FINISHED:
        return ("Done!", "green", deployed_addr)

    raise ValueError("Status was not an accepted status {}".format(list(qresp)[0]))


def is_valid_address(address):
    """
    checks if an address is of the right structure to be an ethereum addresss
    :param address: the address to check
    :return:
    """
    web3_handle = easyweb3.EasyWeb3()
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
    """
    Check if a contract of the name passed exists on disk
    :param contract_name: the name of the contract to check
    :return:
    """
    file_name = constants.CHALLENGE_DIR + contract_name + ".py"

    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        print("Challenge validator not found for contract: " + contract_name)
        return False
    else:
        return True

def get_bytecode_abi(contract_name):
    """
    Get the bytecode and the Application Binary Interface required to deploy a contract
    :param contract_name: the name of the contract on disk to get the abi+bytecode for
    :return: A tuple consisting of the ABI as a string and the bytecode as a string
    """
    if not contract_exists(contract_name):
        raise FileNotFoundError("challenges/" + contract_name + ".py")
    abi_return = None
    bytecode_return = None

    abi_file_name = constants.CHALLENGE_DIR + contract_name + ".abi"
    with open(abi_file_name, "r") as readfile:
        abi_return = readfile.read()
    bytecode_file_name = constants.CHALLENGE_DIR + contract_name + ".bin"
    with open(bytecode_file_name, "r") as readfile2:
        bytecode_return = readfile2.read()

    return bytecode_return, abi_return


def get_icontract(address, contract_name, contract_address=None):
    if contract_address is None:
        contract_address = get_status(address, contract_name)[2].strip()

    if not contract_exists(contract_name):
        raise FileNotFoundError("challenges/" + contract_name + ".py")

    file_name = constants.CHALLENGE_DIR + contract_name + ".py"

    # Load the file
    loader = importlib.machinery.SourceFileLoader("contract", file_name)
    module = types.ModuleType(loader.name)

    loader.exec_module(module)

    # Setup / reconstruct the EasyWeb3 object for this contract
    contract = module.Contract()
    contract.contract_address = contract_address
    contract.user_address = address
    contract.eweb3 = easyweb3.EasyWeb3()
    contract.eweb3._deployed_address = contract_address
    contract.eweb3._status = "deployed"
    bytecode, abi = get_bytecode_abi(contract_name)
    contract.contract_object = contract.eweb3._web3.eth.contract(abi=abi, address=contract_address)
    return contract

