import os
from unittest import TestCase
import re
import json
import yaml

from flask.ext.webtest import TestApp
import requests_mock

from servicebook.server import create_app


class FrontEndTest(TestCase):
    def setUp(self):
        self.app = TestApp(create_app(True, 'sqlite:///:memory:'))

    def test_clicking_around(self):
        r = self.app.get('/')
        first_proj_link = r.html.findAll('a')[2]['href']

        bz_matcher = re.compile('.*bugzilla.*')
        bz_resp = {'bugs': []}
        sw_matcher = re.compile('search.stage.mozaws.net.*')
        yamlf = os.path.join(os.path.dirname(__file__), '__api__.yaml')

        with open(yamlf) as f:
            sw_resp = yaml.load(f.read())

        with requests_mock.Mocker() as m:
            m.get(bz_matcher, text=json.dumps(bz_resp))
            m.get(sw_matcher, text=json.dumps(sw_resp))

            r = r.click(href=first_proj_link)
            self.assertTrue('Karl' in r)
