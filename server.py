import logging
import os
import sys
import traceback
from flask import Flask, request
from handlers.events import EventsHandler
from slackclient import SlackClient

# pylint: disable=C0103
app = Flask(__name__)
events_handler = EventsHandler()
if not app.testing and "SLACK_API_TOKEN" in os.environ:
    events_handler = EventsHandler(SlackClient(os.environ["SLACK_API_TOKEN"]))

# Heroku
if 'DYNO' in os.environ:
    print "Heroku Mode"
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)
else:
    print "Dev Mode"

@app.route('/', methods=['GET'])
def index():
    return 'Hello World'

@app.route('/events', methods=['POST'])
def events():
    '''
    Events like messages
    '''
    resp = events_handler.handle_events(request.json)
    return resp

@app.route('/interactive', methods=['POST'])
def interactive():
    '''
    Any interactions with message buttons, menus, or dialogs
    '''
    return ''

@app.after_request
def after_request(response):
    # This IF avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        app.logger.info(
            '%s %s %s %s\nheader:\n%sdata:\n%s',
            response.status,
            request.method,
            request.scheme,
            request.full_path,
            request.headers,
            request.data)
    return response

@app.errorhandler(Exception)
def exceptions(e):
    tb = traceback.format_exc()
    app.logger.error(
        '%s %s %s\nheader:\n%sdata:\n%s\n\n%s',
        request.method,
        request.scheme,
        request.full_path,
        request.headers,
        request.data,
        tb)
    return "Internal Server Error", 500
