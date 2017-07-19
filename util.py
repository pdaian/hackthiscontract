import os, config

def exists(user):
    if os.path.isdir(config.db_path + user):
        return True
    os.mkdir(config.db_path + user)
    return False

def get_status(user, challenge):
    if not os.path.isdir(config.db_path + user):
        return ("Not Started", "red")
    if not os.path.isfile(config.db_path + user + "/" + challenge):
        return ("Not Started", "red")
    deployed_addr = open(config.db_path + user + "/" + challenge).read().strip()
    if len(deployed_addr) == 0:
        return ("Error (redeploy)", "red")
    if os.path.isfile(config.db_path + user + "/" + challenge + ".done"):
        return ("Done!" + deployed_addr, "green", deployed_addr)
    return ("Deployed", "black", deployed_addr)

def write_address(user, challenge, address):
    open(config.db_path + user + "/" + challenge, 'w').write(address)
