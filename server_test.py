from server import app
import unittest

class ServerTest(unittest.TestCase):
    def setUp(self):
        self.server = app.test_client()

    def test_url_verification(self):
        resp = self.server.post('/events', data={
            "token": "Jhj5dZrVaK7ZwHHjRyZWjbDl",
            "challenge": "3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P",
            "type": "url_verification"
        })
        assert resp.data == '3eZbrw1aBm2rZgRNFdxV2595E9CY3gmdALWMmHkvFXO7tYXAYM8P'

if __name__ == '__main__':
    unittest.main()