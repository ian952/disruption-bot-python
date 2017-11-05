from flask import Flask, request

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Hello World'

@app.route('/events', methods=['POST'])
def events():
    '''
    Events like messages
    '''
    resp = request.form['challenge']
    return resp

@app.route('/interactive', methods=['POST'])
def interactive():
    '''
    Any interactions with message buttons, menus, or dialogs
    '''
    pass
