import os
from collections import deque, defaultdict

class History(object):
    MSG_LIMIT = 10
    FERIDUN = 'FERIDUN'

    def __init__(self):
        self.history = defaultdict(deque)

    def add_message(self, channel, user, text):
        self.history[channel].append({
            'user': user,
            'text': text,
        })
        if len(self.history[channel]) > self.MSG_LIMIT:
            self.history[channel].popleft()

    def has_feridun(self, channel):
        combined_msg = ''

        for item in reversed(self.history[channel]):
            if len(combined_msg) >= len(self.FERIDUN):
                return False
            msg = item['text']
            combined_msg = msg.upper() + combined_msg
            if combined_msg == self.FERIDUN:
                return True
        return False

    def reset(self):
        self.history = defaultdict(deque)

    def to_dict(self):
        return self.history

class EventsHandler(object):
    def __init__(self):
        self.history = History()
        self.slack_client = None

    def set_slack_client(self, slack_client):
        self.slack_client = slack_client

    def get_history(self):
        return self.history.to_dict()

    def reset_history(self):
        self.history.reset()

    def handle_events(self, request):
        if request['type'] == 'url_verification':
            return request['challenge']
        if request['type'] == 'event_callback':
            if request['event']['type'] == 'message':
                event = request['event']
                self.history.add_message(event['channel'], event['user'], event['text'])
                if self.history.has_feridun(event['channel']):
                    print 'feridun'
                    self.send_feridun_message(event['channel'])
        return ''

    def send_feridun_message(self, channel):
        if self.slack_client:
            from server import app
            resp = self.slack_client.api_call(
                'chat.postMessage',
                channel=channel,
                text='DISRUPTIVE!!!'
            )
            if resp['ok'] != True:
                app.logger.error('Message send failed: %s', resp)
        else:
            print "Debug Slack API Call: %s, channel=%s, text=\"%s\"" % \
                    ('chat.postMessage', channel, 'DISRUPTIVE!!!')
