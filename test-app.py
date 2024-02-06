import unittest
from quart import Quart, testing
import app  # Importieren Sie Ihre Anwendung

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.app  # Zugriff auf die Anwendung aus Ihrer app.py-Datei
        self.client = self.app.test_client()

    async def test_ping_pong(self):
        response = await self.client.get('/ping')
        data = await response.get_data()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data, b'pong!')

if __name__ == '__main__':
    unittest.main()