import os
from functools import wraps

from flask import render_template
from web3.utils import validation

import config as constants


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
    deployed_addr = open(constants.DB_PATH + user + "/" + challenge).read().strip()
    if len(deployed_addr) == 0:
        return ("Error (redeploy)", "red")
    if os.path.isfile(constants.DB_PATH + user + "/" + challenge + ".done"):
        return ("Done!", "green", deployed_addr)
    return ("Deployed / Unfinished", "black", deployed_addr)


def write_address(user, challenge, address):
    if not os.path.exists(constants.DB_PATH):
        os.mkdir(constants.DB_PATH)  # TODO: Is this working?
    open(constants.DB_PATH + user + "/" + challenge, 'w').write(address)


def mark_finished(user, challenge):
    open(constants.DB_PATH + user + "/" + challenge + '.done', 'w').write("")


def is_valid_address(address):
    return validation.is_address(address)


def check_address_decorator(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        address = kwargs['address']
        if not is_valid_address(address):
            return render_template("error.html")
        return fn(*args, **kwargs)

    return wrapped
