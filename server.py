from flask import Flask, request

# pylint: disable=C0103
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Hello World'

@app.route('/events', methods=['POST'])
def events():
    '''
    Events like messages
    '''
    resp = request.json
    return resp['challenge']

@app.route('/interactive', methods=['POST'])
def interactive():
    '''
    Any interactions with message buttons, menus, or dialogs
    '''
    pass
