from unittest import TestCase
from flask.ext.webtest import TestApp
from servicebook.server import create_app


class FrontEndTest(TestCase):
    def setUp(self):
        self.app = TestApp(create_app(True, 'sqlite:///:memory:'))

    def test_home(self):
        r = self.app.get('/')
        self.assertTrue('WebExtensions' in r)
