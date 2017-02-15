from servicebook.keys import main
from servicebook.db import Session
from servicebook.mappings import AuthenticationKey
from servicebook.tests.support import BaseTest


class TestKeys(BaseTest):

    def test_main(self):
        session = Session()

        main(['add', 'app1'])
        main(['add', 'app1'])
        main(['add', 'app2'])
        keys = session.query(AuthenticationKey).count()
        self.assertEqual(keys, 2)
        main(['revoke', 'app1'])
        main(['list'])
        keys = session.query(AuthenticationKey).count()
        self.assertEqual(keys, 1)
