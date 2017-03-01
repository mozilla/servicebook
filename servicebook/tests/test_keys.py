from servicebook.keys import main
from servicebook.db import Session
from servicebook.mappings import AuthenticationKey
from servicebook.tests.support import BaseTest, silence


class TestKeys(BaseTest):

    def test_main(self):
        session = Session()
        before_keys = session.query(AuthenticationKey).count()

        with silence():
            main(['add', 'app1'])
            main(['add', 'app1'])
            main(['add', 'app2'])

        keys = session.query(AuthenticationKey).count()
        self.assertEqual(keys, before_keys + 2)

        with silence():
            main(['revoke', 'app1'])
            main(['list'])

        keys = session.query(AuthenticationKey).count()
        self.assertEqual(keys, before_keys + 1)
