import importlib.machinery
import importlib.util
import os
import json
import types
from functools import wraps

from flask import render_template, g
import web3

import config as constants
import easyweb3
import sqlite3

def init_db():
    """
    CREATE TABLE init db function. To be run on startup.
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS htctable(
        userid INTEGER PRIMARY KEY,
        useraddress TEXT NOT NULL UNIQUE,
        score INTEGER,
        c0state INTEGER,
        c0deployaddr TEXT,
        c0finished INTEGER,
        c1state INTEGER,
        c1deployaddr TEXT,
        c1finished INTEGER,
        c2state INTEGER,
        c2deployaddr TEXT,
        c2finished INTEGER,
        c3state INTEGER,
        c3deployaddr TEXT,
        c3finished INTEGER,
        c4state INTEGER,
        c4deployaddr TEXT,
        c4finished INTEGER,
        c5state INTEGER,
        c5deployaddr TEXT,
        c5finished INTEGER,
        c6state INTEGER,
        c6deployaddr TEXT,
        c6finished INTEGER,
        c7state INTEGER,
        c7deployaddr TEXT,
        c7finished INTEGER
    );"""
    htcdb = get_db()
    cur = htcdb.execute(create_table_sql)
    htcdb.commit()

def get_db():
    """
    gets the DB from the flask global context.
    :param user: user address to check against
    :return: whether or not the user is in our database
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(constants.DB_PATH)
        db.row_factory = sqlite3.Row
    return db

def get_db_no_app_context():
    """
    just gets a connection to the db with no global context.
    Why would we want to do this? Because flask is a stupid pos that doesn't work
    and throws "RuntimeError: Working outside of application context." completely
    randomly and in a totally non-deterministic way. So sometimes, it's ok to access
    the global context, and other times it'll throw.

    So now we just have multiple ways to get at the bloody db, and we try to share
    as much as we can.
    :param user: user address to check against
    :return: whether or not the user is in our database
    """
    db = sqlite3.connect(constants.DB_PATH)
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
            c0state,
            c0finished,
            c1state,
            c1finished,
            c2state,
            c2finished,
            c3state,
            c3finished,
            c4state,
            c4finished,
            c5state,
            c5finished,
            c6state,
            c6finished,
            c7state,
            c7finished
        ) VALUES (
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
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
            False,
            constants.STATE_NOT_STARTED,
            False,
            constants.STATE_NOT_STARTED,
            False,
            constants.STATE_NOT_STARTED,
            False,
            constants.STATE_NOT_STARTED,
            False,
            constants.STATE_NOT_STARTED,
            False,
            constants.STATE_NOT_STARTED,
            False,
            constants.STATE_NOT_STARTED,
            False
        ))
        htcdb.commit()
        return False

    return True


def erase_challenge_deployed_address_from_db(user, challenge_number):
    """
    Deletes a users deployed contract address from the db. Used for redeployment.
    :param user: user address to write
    :param challenge_number: which challenge they're working on
    :param address: address of the deployed challenge contract for this user
    """
    exists(user)
    deployed_addr_column_name = "c" + str(int(challenge_number)) + "deployaddr"
    state_column_name = "c" + str(int(challenge_number)) + "state"
    htcdb = get_db()
    print("erasing challenge from db {} {}".format(user, deployed_addr_column_name))
    cur = htcdb.execute("UPDATE htctable SET {0} = ?, {1} = ? WHERE useraddress = ?".format(deployed_addr_column_name, state_column_name),
                        (None, constants.STATE_NOT_STARTED, user))
    htcdb.commit()


def write_address(user, challenge_number, address):
    """
    Writes a user's address into the HackThisContract database
    :param user: user address to write
    :param challenge_number: which challenge they're working on
    :param address: address of the deployed challenge contract for this user
    """
    exists(user)
    deployed_addr_column_name = "c" + str(int(challenge_number)) + "deployaddr"
    state_column_name = "c" + str(int(challenge_number)) + "state"
    htcdb = get_db()
    print("write address to db {} {} {}".format(user, address, deployed_addr_column_name))
    cur = htcdb.execute("UPDATE htctable SET {0} = ?, {1} = ? WHERE useraddress = ?".format(deployed_addr_column_name, state_column_name),
                        (address, constants.STATE_DEPLOYED_IN_PROGRESS, user))
    htcdb.commit()

def get_deployed_contract_address_for_challenge(user, challenge_number):
    """
    Reads the deployed contract address from the HackThisContract database
    :param user: user address to lookup for
    :param challenge_number: which challenge they're working on
    :return address: address of the deployed challenge contract for this user
    """
    exists(user)
    deployed_addr_column_name = "c" + str(int(challenge_number)) + "deployaddr"
    state_column_name = "c" + str(int(challenge_number)) + "state"
    htcdb = get_db()
    cur = htcdb.execute("SELECT {},{} FROM htctable WHERE useraddress = ?".format(deployed_addr_column_name, state_column_name),
                        (user, ))
    # there should always only be one row. This is still wierd syntax, I know
    for row in cur:
        assert(row[1] == constants.STATE_DEPLOYED_IN_PROGRESS)
        return row[0]

def mark_in_progress(user, challenge_number):
    """
    Mark a challenge as deployed / in progress in the HackThisContract Database
    :param user: user address that completed the challenge
    :param challenge_number: which challenge
    :return:
    """
    #exists(user)
    state_column_name = "c" + str(int(challenge_number)) + "state"
    htcdb = get_db_no_app_context()
    print("mark in progress {} {} {}".format(user, state_column_name))
    cur = htcdb.execute("UPDATE htctable SET {0} = ? WHERE useraddress = ?".format(state_column_name), (constants.STATE_DEPLOYED_IN_PROGRESS, user))
    htcdb.commit()

def mark_grading(user, challenge_number):
    """
    Mark a challenge as in grading progress in the HackThisContract Database
    :param user: user address that completed the challenge
    :param challenge_number: which challenge
    :return:
    """
    #exists(user)
    state_column_name = "c" + str(int(challenge_number)) + "state"
    htcdb = get_db_no_app_context()
    print("mark grading {} {}".format(user, state_column_name))
    cur = htcdb.execute("UPDATE htctable SET {0} = ? WHERE useraddress = ?".format(state_column_name), (constants.STATE_GRADING, user))
    htcdb.commit()

def mark_finished(user, challenge_name):
    """
    Mark a challenge as finished (graded and is correct) in the HackThisContract Database
    :param user: user address that completed the challenge
    :param challenge_number: which challenge
    :return:
    """
    #exists(user)
    challenge_number = get_contract_number(challenge_name)
    state_column_name = "c" + str(int(challenge_number)) + "state"
    finished_column_name = "c" + str(int(challenge_number)) + "finished"
    htcdb = get_db_no_app_context()
    print("mark finished {} {} {}".format(user, finished_column_name))
    cur = htcdb.execute("SELECT {}, score FROM htctable WHERE useraddress = ?".format(finished_column_name),
                        (user, ))
    firstele = cur.fetchone()
    finished = firstele[0]
    if finished == False:
        points = get_points(challenge_name)
        curscore = firstele[1]
        cur = htcdb.execute("UPDATE htctable SET {0} = ?, {1} = ?, score = ? WHERE useraddress = ?".format(state_column_name, finished_column_name), (constants.STATE_FINISHED, True, curscore + points , user))
        htcdb.commit()
    else: # if the challenge has been previously solved do not award points for it
        cur = htcdb.execute("UPDATE htctable SET {0} = ? WHERE useraddress = ?".format(state_column_name), (constants.STATE_FINISHED, user))
        htcdb.commit()

def get_contract_number(contract_name):
    """
    Simple helper function to return the number corresponding to a contract name
    :param contract_name the name of the contract you're working with
    :return number - the number for this contract in the db
    """
    return int(contract_name.split("_")[0])

def get_points(contract_name):
    with open("challenges/" + contract_name + ".json") as f:
        jsonfile = f.read().strip()
        retval = int(json.loads(jsonfile)["level"])
    return retval

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
        return ("Not Started", "red")
    state = list(qresp)[0]
    deployed_addr = list(qresp)[1]
    if state == constants.STATE_NOT_STARTED:
        return ("Not Started", "red")
    elif state == constants.STATE_DEPLOYED_IN_PROGRESS:
        return ("Deployed / Unfinished", "black", deployed_addr)
    elif state == constants.STATE_GRADING:
        return ("Grading", "red", deployed_addr)
    elif state == constants.STATE_FINISHED:
        return ("Done!", "green", deployed_addr)

    raise ValueError("Status was not an accepted status {}".format(list(qresp)[0]))

def get_ranking_from_db():
    htcdb = get_db()
    qresp = query_db("SELECT useraddress, score FROM htctable WHERE score > 0 ORDER BY score DESC", (), False)
    return [(row[0], row[1]) for row in qresp]

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
    file_name = constants.CHALLENGE_DIR + contract_name + ".sol"

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
        raise FileNotFoundError("challenges/" + contract_name + ".sol")
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

