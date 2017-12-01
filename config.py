import os

CHALLENGE_DIR = 'challenges'


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

GETH_DATADIR = '/home/benji/.ethereum/rinkeby'
SOLC_PATH = '/home/benji/compiled/solidity/build/solc/solc'

DEPLOY_FROM_ADDRESS = '0xe4dfd8063d09928a47ef566b249ad227d9f5586d'
DEPLOY_GAS_PRICE = 1000000000

DB_PATH = "/home/benji/hackthiscontractdb/"  # include trailing /

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080
