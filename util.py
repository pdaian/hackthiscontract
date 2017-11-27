import config as constants
import os


def exists(user):
    print("util.exists")
    if os.path.isdir(constants.db_path + user):
        return True
    os.mkdir(constants.db_path + user)
    return False


def get_status(user, challenge):
    print("util.get_status")
    if not os.path.isdir(constants.db_path + user):
        return ("Not Started", "red")
    if not os.path.isfile(constants.db_path + user + "/" + challenge):
        return ("Not Started", "red")
    deployed_addr = open(constants.db_path + user + "/" + challenge).read().strip()
    if len(deployed_addr) == 0:
        return ("Error (redeploy)", "red")
    if os.path.isfile(constants.db_path + user + "/" + challenge + ".done"):
        return ("Done!", "green", deployed_addr)
    return ("Deployed / Unfinished", "black", deployed_addr)


def write_address(user, challenge, address):
    print("util.write_address")
    open(constants.db_path + user + "/" + challenge, 'w').write(address)


def mark_finished(user, challenge):
    print("util.mark_finished")
    open(constants.db_path + user + "/" + challenge + '.done', 'w').write("")
