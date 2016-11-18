from unittest import TestCase
from flask.ext.webtest import TestApp
from servicebook.server import create_app


_ONE_TIME = None


class BaseTest(TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        global _ONE_TIME
        if _ONE_TIME is None:
            _ONE_TIME = TestApp(create_app(True, 'sqlite://'))
        self.app = _ONE_TIME
