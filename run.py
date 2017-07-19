from flask import Flask, render_template, request
import config
import json
app = Flask(__name__)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/dashboard")
def dashboard():
    address = request.args.get("address", None)
    challenges = {}
    for challenge_name in config.challenges:
        challenges[challenge_name] = json.loads(open("challenges/" + challenge_name + ".json").read().strip())
        challenges[challenge_name]["code"] = open("challenges/" + challenge_name + ".sol").read().strip()
    return render_template('dashboard.html', address = address, challenge_names = config.challenges, challenges = challenges)

@app.route("/deploy/<string:contract>")
def deploy(contract):
    return contract

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port='80')

