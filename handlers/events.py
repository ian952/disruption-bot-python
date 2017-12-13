import os
from collections import deque, defaultdict

class History(object):
    MSG_LIMIT = 10
    FERIDUN = 'FERIDUN'
    TERRIBLECODE = ':terriblecode-0-0::terriblecode-1-0::terriblecode-2-0:\n' +\
':terriblecode-0-1::terriblecode-1-1::terriblecode-2-1:\n' +\
':terriblecode-0-2::terriblecode-1-2::terriblecode-2-2:'

    LAST_MSG_RESP = {
        'terriblecode': TERRIBLECODE,
        'outage': TERRIBLECODE,
    }

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

    def get_resp_to_last_msg(self, channel):
        if len(self.history[channel]) > 0:
            last_msg = self.history[channel][-1].lower()
            for k in self.LAST_MSG_RESP:
                if last_msg == k:
                    return self.LAST_MSG_RESP[k]
        return None

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
                channel = event['channel']
                user = None
                if 'user' in event:
                    user = event['user']
                elif 'bot_id' in event:
                    user = event['bot_id']
                text = event['text']

                self.history.add_message(channel, user, text)
                if self.history.has_feridun(channel):
                    self.send_feridun_message(channel)
                resp = self.history.get_resp_to_last_msg(channel)
                if resp is not None:
                    self.send_message(channel, resp)
        return ''

    def send_message(self, channel, msg):
        if self.slack_client:
            from server import app
            resp = self.slack_client.api_call(
                'chat.postMessage',
                channel=channel,
                text=msg
            )
            if resp['ok'] != True:
                app.logger.error('Message send failed: %s', resp)
        else:
            print "Debug Slack API Call: %s, channel=%s, text=\"%s\"" % \
                    ('chat.postMessage', channel, msg)

    def send_feridun_message(self, channel):
        self.send_message(channel, 'DISRUPTIVE!!!')
