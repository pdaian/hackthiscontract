import os

HOMEPATH = os.path.expanduser("~")

CHALLENGE_DIR = '{}/hackthiscontract/challenges/'.format(HOMEPATH)

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
SOLC4_PATH = '{}/solidity4.x/solc'.format(HOMEPATH)

DEPLOY_FROM_ADDRESS = '0xc0fcd7514CBfC90A36E4bB21AD49845A4c3b3D54'
DEPLOY_GAS_PRICE = 1000000000

DB_PATH = "{}/database/".format(HOMEPATH)

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080
