import importlib.machinery
import importlib.util
import json
import os
import types

from flask import Flask, render_template, request, redirect

import config as constants
import ethereum
import util

app = Flask(__name__)

deployers = {}


@app.route("/")
def hello():
    if request.args.get("error", None) is None:
        return render_template('index.html')
    else:
        return render_template('index.html', error=request.args.get("error", None))


@app.route("/dashboard")
def dashboard():
    address = request.args.get("address", None).strip()
    if not util.is_valid_address(address):
        return redirect("/?error=Invalid%20address")
    challenges = {}
    for challenge_id in constants.CHALLENGES:
        challenges[challenge_id] = json.loads(open("challenges/" + challenge_id + ".json").read().strip())
        challenges[challenge_id]["code"] = open("challenges/" + challenge_id + ".sol").read().strip()
        challenges[challenge_id]["status"] = util.get_status(address, challenge_id)
        challenges[challenge_id]["deployed"] = (len(challenges[challenge_id]["status"]) == 3)
    return render_template('dashboard.html', address=address, challenge_ids=constants.CHALLENGES, challenges=challenges,
                           exists=util.exists(address))


def get_status(address, contract):
    global deployers
    deploy_key = address + "|" + contract
    if not deploy_key in deployers:
        web3_instance = ethereum.EasyWeb3()
        deployers[deploy_key] = web3_instance
        web3_instance.unlock_coinbase()
        web3_instance.deploy_named_solidity_contract(contract)
    else:
        web3_instance = deployers[deploy_key]
    return web3_instance.deploy_status()


@app.route("/done/<string:address>/<string:contract>")
def done(address, contract):
    status = get_status(address, contract)
    if status[1] is not None:
        util.write_address(address, contract, status[1])
    return status[0]


@app.route("/deploy/<string:address>/<string:contract>")
def deploy(address, contract):
    status = util.get_status(address, contract)
    if "not started" in status[0].lower():
        return render_template('deploy.html', deployed=False, address=address, contract=contract)
    else:
        contract_code = open("challenges/" + contract + ".sol").read().strip()
        contract_desc = json.loads(open("challenges/" + contract + ".json").read().strip())["description"]
        return render_template('deploy.html', deployed=True, done=("done" in status[0].lower()), status=status,
                               address=address, contract=contract, contract_code=contract_code,
                               contract_desc=contract_desc)


@app.route("/update/<string:address>/<string:contract_name>")
def update(address, contract_name):
    file_name = "challenges/" + contract_name + ".py"
    contract_addr = util.get_status(address, contract_name)[2].strip()
    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        print("Challenge validator not found for contract: " + contract_name)
        return redirect(request.referrer)

    # Load the file
    loader = importlib.machinery.SourceFileLoader("validator", file_name)
    module = types.ModuleType(loader.name)

    loader.exec_module(module)

    # Setup
    contract = module.Contract()
    contract.contract_address = contract_addr
    contract.user_address = address

    # Validate
    if contract.has_been_hacked():
        util.mark_finished(address, contract_name)

    return redirect(request.referrer)
    # return redirect("/dashboard?address=" + address)


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=constants.SERVER_HOST, port=constants.SERVER_PORT)
