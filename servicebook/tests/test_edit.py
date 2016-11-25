import os
import re
import json
from contextlib import contextmanager

import yaml
import requests_mock
from webtest.app import AppError

from servicebook.tests.support import BaseTest


class EditTest(BaseTest):

    @contextmanager
    def _logged_in(self):
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

        with requests_mock.Mocker() as m:
            m.post(github_matcher, text=github_resp)
            m.get(github_usermatcher, json=github_user)
            m.get(bz_matcher, text=json.dumps(bz_resp))
            m.get(sw_matcher, text=json.dumps(sw_resp))
            self.app.get('/github/callback?code=%s' % code)

            # at this point we are logged in
            try:
                yield
            finally:
                # logging out
                self.app.get('/logout')

    def test_edit_project(self):

        # first attempt fails since we're not logged in
        self.assertRaises(AppError, self.app.get, '/projects/1/edit')

        # now logging in
        with self._logged_in():
            project = self.app.get('/projects/1/edit')
            form = project.forms[0]
            old_name = form['name'].value
            form['name'] = 'new name'
            form.submit()

            # let's check it changed
            self.assertTrue(b'new name' in self.app.get('/projects/1').body)

            # change it back to the old value
            project = self.app.get('/projects/1/edit')
            form = project.forms[0]
            form['name'] = old_name
            form.submit()
