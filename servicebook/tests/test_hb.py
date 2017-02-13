from servicebook.tests.support import BaseTest
from servicebook import __version__


class HBTest(BaseTest):
    def test_version(self):
        info = self.app.get('/__version__').json
        self.assertEqual(info['version'], __version__)

    def test_lbheartbeat(self):
        self.app.get('/__lbheartbeat__', status=200)

    def test_heartbeat(self):
        resp = self.app.get('/__heartbeat__', status=200).json
        self.assertTrue(resp['database'])
