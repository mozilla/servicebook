import json
from servicebook.tests.support import BaseTest


class ActionsTest(BaseTest):

    def test_run_action_hb(self):
        hb = {'ok': 1}
        endpoint = 'mock://heartbeat'
        mockers = [['GET', endpoint, json.dumps(hb)]]

        with self.logged_in(extra_mocks=mockers):
            hb = self.app.get('/actions/heartbeat?endpoint=%s' % endpoint)

        self.assertEqual(hb.json, {'ok': 1})
        self.assertEqual(hb.status_code, 200)

    def test_run_action_smoke(self):
        hb = {'ok': 1}
        endpoint = 'search.stage.mozaws.net/'
        mockers = [['GET', endpoint, json.dumps(hb)]]

        with self.logged_in(extra_mocks=mockers):
            smoke = self.app.get('/actions/smoke?endpoint=%s' % endpoint)

        steps = smoke.json['steps']
        self.assertTrue(all([step['result'] == 'OK' for step in steps]))
        self.assertEqual(smoke.status_code, 200)
