import json

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


@app.route("/update/<string:address>/<string:contract>")
def update(address, contract):
    contract_addr = util.get_status(address, contract)[2].strip()
    checks = json.loads(open("challenges/" + contract + ".json").read().strip()).get("post_check", [])
    contract_bal = ethereum.EasyWeb3().balance(contract_addr)
    for check in checks:
        print(50000000000000000, contract_bal, int(check["balance_lt"]))
        print(type(int(check["balance_lt"])), type(contract_bal))
        if "balance_lt" in check:
            if int(check["balance_lt"]) <= int(contract_bal):
                print(50000000000000000, contract_bal, int(check["balance_lt"]))
                return redirect(request.referrer)
                # return redirect("/dashboard?address=" + address)
    util.mark_finished(address, contract)
    return redirect(request.referrer)
    # return redirect("/dashboard?address=" + address)


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=constants.SERVER_HOST, port=constants.SERVER_PORT)
