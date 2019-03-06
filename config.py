import os

HOMEPATH = os.path.expanduser("~")

# Absolute path breaks unit tests
# CHALLENGE_DIR = '{}/hackthiscontract/challenges/'.format(HOMEPATH)
CHALLENGE_DIR = '{}/challenges/'.format(os.path.abspath('.'))

def find_challenges():
    challenges = []
    array = os.listdir(CHALLENGE_DIR)
    json = []
    sol = []
    for file in array:
        if file.endswith(".json"):
            json.append(file.replace(".json", ""))
        if file.endswith(".sol"):
            sol.append(file.replace(".sol", ""))
    for s in json:
        if s in sol:
            challenges.append(s)
    challenges = sorted(challenges)
    for i in range(0, len(challenges)):
        challenges[i] = str(challenges[i])
    return challenges

CHALLENGES = find_challenges()

GETH_DATADIR = '{}/geth_rinkeby/'.format(HOMEPATH)

DEPLOY_FROM_ADDRESS = '0xc0fcd7514CBfC90A36E4bB21AD49845A4c3b3D54'
DEPLOY_GAS_PRICE = 1000000000

DB_PATH = "{}/hackthiscontract.db".format(HOMEPATH)

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

STATE_NOT_STARTED = 0
STATE_DEPLOYED_IN_PROGRESS = 1
STATE_FINISHED = 2
