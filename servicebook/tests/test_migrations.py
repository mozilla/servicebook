import os
import shutil
from unittest import TestCase

from servicebook.db import migrate_db, Session, DATABASE_VERSION
from servicebook import mappings
from servicebook.tests.support import silence


_DB = os.path.join(os.path.dirname(__file__), 'projects_0.db')
_SQLURI = 'sqlite:////' + _DB


class TestMigration(TestCase):
    def setUp(self):
        super(TestMigration, self).setUp()
        shutil.copyfile(_DB, _DB + '.saved')

    def tearDown(self):
        shutil.copyfile(_DB + '.saved', _DB)
        super(TestMigration, self).tearDown()

    def test_migrate_db(self):
        session = Session()
        with silence():
            migrate_db(['--sqluri', _SQLURI])
        ver = session.query(mappings.DatabaseVersion).one().version
        self.assertEqual(ver, DATABASE_VERSION)
