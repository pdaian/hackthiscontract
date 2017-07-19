from flask import Flask, render_template, request
import config, util
import json
import ethereum
app = Flask(__name__)

deployers = {}

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():
    address = request.args.get("address", None).strip()
    if "|" in address:
        return "Error" # todo full validation
    challenges = {}
    for challenge_id in config.challenges:
        challenges[challenge_id] = json.loads(open("challenges/" + challenge_id + ".json").read().strip())
        challenges[challenge_id]["code"] = open("challenges/" + challenge_id + ".sol").read().strip()
        challenges[challenge_id]["status"] = util.get_status(address, challenge_id)
        challenges[challenge_id]["deployed"] = (len(challenges[challenge_id]["status"]) == 3)
    return render_template('dashboard.html', address = address, challenge_ids = config.challenges, challenges = challenges, exists=util.exists(address))

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
        return render_template('deploy.html', done=False, address=address, contract=contract)
    else:
        contract_code = open("challenges/" + contract + ".sol").read().strip()
        return render_template('deploy.html', done=True, contract_addr=status[2], address=address, contract=contract, contract_code=contract_code)

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port='80')

