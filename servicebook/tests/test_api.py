import os
import re
import json
import yaml

import requests_mock
from servicebook.tests.support import BaseTest


class ApiTest(BaseTest):
    def test_get_table_lists(self):
        tables = self.app.get('/api/').json
        models = tables['models']
        self.assertTrue(len(models) > 3)

    def test_browsing_project(self):
        projects = self.app.get('/api/project').json['data']
        absearch_id = projects[0]['id']

        bz_matcher = re.compile('.*bugzilla.*')
        bz_resp = {'bugs': []}
        sw_matcher = re.compile('search.stage.mozaws.net.*')
        yamlf = os.path.join(os.path.dirname(__file__), '__api__.yaml')

        with open(yamlf) as f:
            sw_resp = yaml.load(f.read())

        with requests_mock.Mocker() as m:
            m.get(bz_matcher, text=json.dumps(bz_resp))
            m.get(sw_matcher, text=json.dumps(sw_resp))
            absearch = self.app.get('/api/project/%d' % absearch_id)
            self.assertEqual(absearch.json['data']['qa_primary_id'], 1)

    def test_langs(self):
        self._test_one_many('language', ('python', 'go', 'javascript'))

    def test_tags(self):
        self._test_one_many('tag', ('python', 'oss', 'watnot'))

    def _test_one_many(self, field_name, collection):
        resp = self.app.get('/api/project/1')
        project = resp.json['data']
        etag = resp.etag

        # create new tags
        elms = []
        req_data = {'data': {'type': field_name,
                             'attributes': {}}}
        headers = {'Content-Type': 'application/vnd.api+json'}
        for elm in collection:
            req_data['data']['attributes']['name'] = elm
            resp = self.app.post_json('/api/' + field_name, params=req_data,
                                      headers=headers)
            elms.append({'type': field_name, 'id': resp.json['data']['id']})

        # patching the projects' tag list
        req_data = {'data': elms}
        headers = {'If-Match': etag,
                   'Content-Type': 'application/vnd.api+json'}

        url = '/api/project/1/relationships/' + field_name + 's'
        self.app.patch_json(url, params=req_data, headers=headers)

        resp = self.app.get('/api/project/1')
        project = resp.json['data']
        self.assertEqual(len(project[field_name + 's']), len(collection))

    def test_browsing_user(self):
        karl_json = self.app.get('/api/user/2').json['data']
        self.assertEqual(karl_json['firstname'], 'Karl')

    def test_browsing_group(self):
        group = self.app.get('/api/group/Customization').json['data']
        self.assertEqual(group['name'], 'Customization')

    def test_changing_user_strict(self):
        resp = self.app.get('/api/user/2')
        etag = resp.etag
        karl_json = resp.json['data']
        old_name = karl_json['firstname']
        new_name = karl_json['firstname'] = old_name + 'something'
        del karl_json['team']
        del karl_json['secondary_team']

        req_data = {'data': {'type': 'user', 'attributes': karl_json,
                    'id': '2'}}

        headers = {'Content-Type': 'application/vnd.api+json'}

        # fails if no If-Match provided
        self.app.patch_json('/api/user/2', params=req_data,
                            headers=headers, status=428)

        # fails if wront etag provided
        headers['If-Match'] = "bleh"
        self.app.patch_json('/api/user/2', params=req_data,
                            headers=headers, status=412)

        headers['If-Match'] = etag
        self.app.patch_json('/api/user/2', params=req_data,
                            headers=headers)

        resp = self.app.get('/api/user/2')
        karl_json = resp.json['data']
        etag = resp.etag
        self.assertEqual(karl_json['firstname'], new_name)

        # now test the etag value
        resp = self.app.get('/api/user/2',
                            headers={'If-None-Match': str(etag)})
        self.assertEqual(resp.status_int, 304)
        self.app.get('/api/user/2', headers={'If-None-Match': "MEH"})

    def test_changing_user(self):
        resp = self.app.get('/api/user/2')
        karl_json = resp.json['data']
        etag = resp.etag
        self.assertEqual(karl_json['firstname'], 'Karl')
        karl_json['firstname'] = 'K.'
        del karl_json['team']
        del karl_json['secondary_team']
        req_data = {'data': {'type': 'user', 'attributes': karl_json,
                    'id': '2'}}
        headers = {'Content-Type': 'application/vnd.api+json',
                   'If-Match': etag}

        self.app.patch_json('/api/user/2', params=req_data,
                            headers=headers)
        resp = self.app.get('/api/user/2')
        karl_json = resp.json['data']
        self.assertEqual(karl_json['firstname'], 'K.')

    def test_search(self):
        resp = self.app.get('/api/search?q=test')
        data = resp.json
        self.assertTrue(len(data['data']) > 0)

    def test_cascade_timestamps(self):
        resp = self.app.get('/api/project/1')
        project_etag = resp.etag
        project_tags = resp.json['data']['tags']

        # changing the relation
        resp = self.app.get('/api/project/1/tags')
        etag = resp.etag

        self.assertEqual(etag, project_etag)

        # removing a tag
        project_tags = project_tags[1:]
        req_data = []
        for tag in project_tags:
            entry = {'type': 'tag', 'id': tag['id']}
            req_data.append(entry)

        req_data = {'data': req_data}
        headers = {'If-Match': etag,
                   'Content-Type': 'application/vnd.api+json'}
        self.app.patch_json('/api/project/1/relationships/tags',
                            params=req_data, headers=headers)

        # the project etag should have changed
        resp = self.app.get('/api/project/1')
        self.assertNotEqual(project_etag, resp.etag)
