import unittest
from collections import deque
from server import app, events_handler
from handlers.events import History
from mock import Mock
import ujson

class ServerTest(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.server = app.test_client()
        self.mock_slack_api = Mock(return_value={'ok': True})
        events_handler.set_slack_client(self.mock_slack_api)

    def tearDown(self):
        events_handler.reset_history()

    def test_url_verification(self):
        resp = self.server.post(
            '/events',
            headers={'content-type': 'application/json'},
            data=ujson.dumps({
                "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
                "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P",
                "type": "url_verification"
            })
        )
        assert resp.data == '3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P'

    def post_msg_event(self, msg):
        self.server.post(
            '/events',
            headers={'content-type': 'application/json'},
            data=ujson.dumps({
                "token": "z26uFbvR1xHJEdHE1OQiO6t8",
                "team_id": "T061EG9RZ",
                "api_app_id": "A0FFV41KK",
                "event": {
                    "type": "message",
                    "user": "U7USK5RCL",
                    "text": msg,
                    "ts": "1510460963.000071",
                    "channel": "D7V8VFEUD",
                    "event_ts": "1510460963.000071"
                },
                "event_ts": "1465244570.336841",
                "type": "event_callback",
                "authed_users": [
                    "U061F7AUR"
                ]
            })
        )

    def test_nonferidun_message_event(self):
        self.post_msg_event('eridun')
        self.mock_slack_api.api_call.assert_not_called()
        assert events_handler.get_history()['D7V8VFEUD'] == \
                deque([{'text': 'eridun', 'user': 'U7USK5RCL'}])

    def test_feridun_message(self):
        self.post_msg_event('feridun')
        self.mock_slack_api.api_call.assert_called_once_with(
            'chat.postMessage',
            channel="D7V8VFEUD",
            text='DISRUPTIVE!!!'
        )
        assert events_handler.get_history()['D7V8VFEUD'] == \
                deque([{'text': 'feridun', 'user': 'U7USK5RCL'}])

    def test_partial_feridun_message(self):
        self.post_msg_event('f')
        self.post_msg_event('f')
        self.post_msg_event('e')
        self.post_msg_event('f')
        self.post_msg_event('E')
        self.post_msg_event('r')
        self.post_msg_event('i')
        self.post_msg_event('D')
        self.post_msg_event('u')
        self.post_msg_event('n')
        self.post_msg_event('f')

        self.mock_slack_api.api_call.assert_called_once_with(
            'chat.postMessage',
            channel="D7V8VFEUD",
            text='DISRUPTIVE!!!'
        )

    def test_single_message_is_special(self):
        self.post_msg_event('outage')

        self.mock_slack_api.api_call.assert_called_once_with(
            'chat.postMessage',
            channel="D7V8VFEUD",
            text=History.TERRIBLECODE
        )

    def test_bot_message(self):
        resp = self.server.post(
            '/events',
            headers={'content-type': 'application/json'},
            data=ujson.dumps({
                "token": "z26uFbvR1xHJEdHE1OQiO6t8",
                "team_id": "T061EG9RZ",
                "api_app_id": "A0FFV41KK",
                "event": {
                    "type": "message",
                    "bot_id": "U7USK5RCL",
                    "text": 'DISRUPTIVE!!!',
                    "ts": "1510460963.000071",
                    "channel": "D7V8VFEUD",
                    "event_ts": "1510460963.000071"
                },
                "event_ts": "1465244570.336841",
                "type": "event_callback",
                "authed_users": [
                    "U061F7AUR"
                ]
            })
        )
        assert resp.status_code == 200

if __name__ == '__main__':
    unittest.main()
