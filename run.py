import json
import os

from flask import Flask, render_template, request, redirect

import config as constants
import easyweb3
import util

app = Flask(__name__)

deployers = {}


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/dashboard/<string:address>")
@util.check_address_decorator
def dashboard(address):
    challenges = {}
    for challenge_id in constants.CHALLENGES:
        challenges[challenge_id] = json.loads(open("challenges/" + challenge_id + ".json").read().strip())
        challenges[challenge_id]["code"] = open("challenges/" + challenge_id + ".sol").read().strip()
        challenges[challenge_id]["status"] = util.get_status(address, challenge_id)
        challenges[challenge_id]["deployed"] = (len(challenges[challenge_id]["status"]) == 3)
    return render_template('dashboard.html', address=address, challenge_ids=constants.CHALLENGES, challenges=challenges,
                           exists=util.exists(address))


@util.check_address_decorator
def get_status(address, contract):
    global deployers
    deploy_key = (address, contract)
    if not deploy_key in deployers:
        web3_instance = easyweb3.EasyWeb3()
        deployers[deploy_key] = web3_instance
        web3_instance.deploy_named_solidity_contract(contract, address)
    else:
        web3_instance = deployers[deploy_key]
    return web3_instance.deploy_status()


@app.route("/done/<string:address>/<string:contract>")
@util.check_address_decorator
def done(address, contract):
    print("Done:\t" + address)
    status = get_status(address, contract)

    if status[1] is not None and status[0] == "deployed":
        print("Status is not none: " + str(status))
        global deployers
        deploy_key = (address, contract)
        del deployers[deploy_key]
        util.write_address(address, contract, status[1])
    if status[0]:
        return status[0]
    else:
        return "Starting deployment process"


@app.route("/deploy/<string:address>/<string:contract>", methods=['POST'])
@util.check_address_decorator
def deploy(address, contract):
    status = util.get_status(address, contract)
    if "not started" in status[0].lower():
        return render_template('deploy.html', deployed=False, address=address, contract=contract)
    else:
        return redirect("/view/" + address + "/" + contract)


@app.route("/view/<string:address>/<string:contract>")
@util.check_address_decorator
def view(address, contract):
    status = util.get_status(address, contract)
    if "not started" in status[0].lower():
        return "Not started!"
    contract_code = open("challenges/" + contract + ".sol").read().strip()
    contract_desc = json.loads(open("challenges/" + contract + ".json").read().strip())["description"]
    return render_template('view.html', deployed=True, done=("done" in status[0].lower()), status=status,
                           address=address, contract=contract, contract_code=contract_code,
                           contract_desc=contract_desc)


@app.route("/update/<string:address>/<string:contract_name>")
@util.check_address_decorator
def update(address, contract_name):
    file_name = "challenges/" + contract_name + ".py"
    contract_addr = util.get_status(address, contract_name)[2].strip()
    if not os.path.exists(file_name) or not os.path.isfile(file_name):
        print("Challenge validator not found for contract: " + contract_name)
        return redirect(request.referrer)

    contract = util.get_contract(address, contract_name, contract_address=contract_addr)

    # Validate
    if contract.has_been_hacked():
        util.mark_finished(address, contract_name)

    return redirect(request.referrer)


@app.route("/redeploy/<string:address>/<string:contract_name>", methods=['POST'])
@util.check_address_decorator
def redeploy(address, contract_name):
    if (os.path.isfile(constants.DB_PATH + address + "/" + contract_name)):
        os.remove(constants.DB_PATH + address + "/" + contract_name)
    if (os.path.isfile(constants.DB_PATH + address + "/" + contract_name + ".done")):
        os.remove(constants.DB_PATH + address + "/" + contract_name + ".done")
    return deploy(address, contract_name)


@app.route("/ranking")
def ranking():
    users = []
    for address in os.listdir(constants.DB_PATH):
        done = 0
        for filename in os.listdir(constants.DB_PATH + address):
            if filename.endswith(".done"):
                done += 1
        data = {"address": address, "solved": done}
        if not done == 0:
            users.append(data)

    users.sort(key=lambda x: x['solved'], reverse=True)
    counter = 0
    largest = 1e29
    for user in users:
        if user['solved'] < largest:
            counter += 1
            largest = user['solved']
        user['pos'] = counter
    return render_template("ranking.html", users=users)


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=constants.SERVER_HOST, port=constants.SERVER_PORT)
