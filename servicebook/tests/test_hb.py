from servicebook.tests.support import BaseTest
from servicebook import __version__


class HBTest(BaseTest):
    def test_version(self):
        info = self.app.get('/__version__').json
        self.assertEqual(info['version'], __version__)
