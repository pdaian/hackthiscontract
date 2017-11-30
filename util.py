import os

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
    open(constants.DB_PATH + user + "/" + challenge, 'w').write(address)


def mark_finished(user, challenge):
    open(constants.DB_PATH + user + "/" + challenge + '.done', 'w').write("")
