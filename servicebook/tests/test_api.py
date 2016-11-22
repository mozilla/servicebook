import os
import re
import json
import yaml

import requests_mock
from servicebook.tests.support import BaseTest


class ApiTest(BaseTest):

    def test_browsing_project(self):
        absearch_id = self.app.get('/projects.json').json[0]['id']

        bz_matcher = re.compile('.*bugzilla.*')
        bz_resp = {'bugs': []}
        sw_matcher = re.compile('search.stage.mozaws.net.*')
        yamlf = os.path.join(os.path.dirname(__file__), '__api__.yaml')

        with open(yamlf) as f:
            sw_resp = yaml.load(f.read())

        with requests_mock.Mocker() as m:
            m.get(bz_matcher, text=json.dumps(bz_resp))
            m.get(sw_matcher, text=json.dumps(sw_resp))
            absearch = self.app.get('/project/%d.json' % absearch_id)
            self.assertEqual(absearch.json['primary_id'], 3)

    def test_browsing_user(self):
        karl_json = self.app.get('/person/3.json').json
        projects = [proj['name'] for proj in karl_json['projects']]
        projects.sort()
        wanted = ['ABSearch', 'Balrog', 'Firefox Accounts', 'Kinto',
                  'NoMore404s', 'SHIELD', 'Sync']
        self.assertEqual(projects, wanted)

    def test_browsing_group(self):
        group = self.app.get('/group/Customization.json').json
        projs = [p['name'] for p in group['projects']]
        self.assertTrue('Telemetry' in projs)
