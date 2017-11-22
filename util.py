import os, config

def exists(user):
    print("util.exists")
    if os.path.isdir(config.db_path + user):
        return True
    os.mkdir(config.db_path + user)
    return False

def get_status(user, challenge):
    print("util.get_status")
    if not os.path.isdir(config.db_path + user):
        return ("Not Started", "red")
    if not os.path.isfile(config.db_path + user + "/" + challenge):
        return ("Not Started", "red")
    deployed_addr = open(config.db_path + user + "/" + challenge).read().strip()
    if len(deployed_addr) == 0:
        return ("Error (redeploy)", "red")
    if os.path.isfile(config.db_path + user + "/" + challenge + ".done"):
        return ("Done!", "green", deployed_addr)
    return ("Deployed / Unfinished", "black", deployed_addr)

def write_address(user, challenge, address):
    print("util.write_address")
    open(config.db_path + user + "/" + challenge, 'w').write(address)

def mark_finished(user, challenge):
    print("util.mark_finished")
    open(config.db_path + user + "/" + challenge + '.done', 'w').write("")
