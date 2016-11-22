import os
from unittest import TestCase

from flask.ext.webtest import TestApp
from servicebook.server import create_app


_ONE_TIME = None
_DUMP = os.path.join(os.path.dirname(__file__), '..', 'dump.json')


class BaseTest(TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        global _ONE_TIME
        if _ONE_TIME is None:
            _ONE_TIME = TestApp(create_app('sqlite://', _DUMP))
        self.app = _ONE_TIME
