import os
from unittest import TestCase
from contextlib import contextmanager
import json
import re

import yaml
import requests_mock
from flask.ext.webtest import TestApp
from servicebook.server import main as app_creator
from servicebook.db import main as importer


_ONE_TIME = None
_DUMP = os.path.join(os.path.dirname(__file__), '..', 'dump.json')
_INI = os.path.join(os.path.dirname(__file__), 'servicebook.ini')


class BaseTest(TestCase):
    def setUp(self):
        super(BaseTest, self).setUp()
        global _ONE_TIME
        if _ONE_TIME is None:
            importer(['--dump-file', _DUMP, '--sqluri', 'sqlite://'])
            app = app_creator(['--config-file', _INI, '--no-run'])
            _ONE_TIME = TestApp(app)
        self.app = _ONE_TIME

    @contextmanager
    def logged_in(self, extra_mocks=None):
        if extra_mocks is None:
            extra_mocks = []

        # let's log in
        self.app.get('/login')
        # redirects to github, let's fake the callback
        code = 'yeah'
        github_resp = 'access_token=yup'
        github_user = {'login': 'tarekziade', 'name': 'Tarek Ziade'}
        github_matcher = re.compile('github.com/')
        github_usermatcher = re.compile('https://api.github.com/user')
        bz_matcher = re.compile('.*bugzilla.*')
        bz_resp = {'bugs': []}
        sw_matcher = re.compile('search.stage.mozaws.net.*')

        yamlf = os.path.join(os.path.dirname(__file__), '__api__.yaml')
        with open(yamlf) as f:
            sw_resp = yaml.load(f.read())

        headers = {'Content-Type': 'application/json'}
        with requests_mock.Mocker() as m:
            m.post(github_matcher, text=github_resp)
            m.get(github_usermatcher, json=github_user)
            m.get(bz_matcher, text=json.dumps(bz_resp))
            m.get(sw_matcher, text=json.dumps(sw_resp))
            self.app.get('/github/callback?code=%s' % code)
            for verb, url, text in extra_mocks:
                m.register_uri(verb, re.compile(url), text=text,
                               headers=headers)

            # at this point we are logged in
            try:
                yield
            finally:
                # logging out
                self.app.get('/logout')
