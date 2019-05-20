from flask import Flask

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'The site is being updated right now and or is down for maintenance. We appreciate your patience. Our apologies!'

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['PREFERRED_URL_SCHEME'] = 'https'
    app.run(host=constants.SERVER_HOST, port=constants.SERVER_PORT)
