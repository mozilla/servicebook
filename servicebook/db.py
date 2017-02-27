# encoding: utf8
import os
import json
import argparse
import sys
import random

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.orm.exc import NoResultFound

from servicebook import mappings
from servicebook.search import get_indexer
from servicebook.migrations import increment_database


session_factory = sessionmaker(autoflush=False)
Session = scoped_session(session_factory)
here = os.path.dirname(__file__)
_DUMP = os.path.join(here, 'dump.json')
_SQLURI = os.environ.get('SQLURI', 'sqlite:////tmp/qa_projects.db')
_SEARCH = {"WHOOSH_BASE": "/tmp/whoosh-" + str(sys.hexversion)}
DATABASE_VERSION = 1


def _migrate(engine, current, target):
    print("Migrating from %s to %s" % (current, target))
    session = Session()
    while current < target:
        current = increment_database(engine, session, current)
        session.commit()

    version = session.query(mappings.DatabaseVersion).first()
    if version is None:
        version = mappings.DatabaseVersion()
    version.version = target
    session.add(version)
    session.commit()
    print("Done")


def migrate_db(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='ServiceBook Data importer.')

    parser.add_argument('--sqluri', help='Database',
                        type=str, default=_SQLURI)

    args = parser.parse_args(args=args)
    engine = init(args.sqluri)
    session = Session()

    # read the database version
    try:
        version = session.query(mappings.DatabaseVersion).one().version
    except NoResultFound:
        version = 0
    print("Current Database version %d" % version)
    print("Target Database version %d" % DATABASE_VERSION)

    if version < DATABASE_VERSION:
        _migrate(engine, version, DATABASE_VERSION)
    else:
        print("Nothing will be done.")


def init(sqluri=_SQLURI, dump=None):
    engine = create_engine(sqluri)
    session_factory.configure(bind=engine)
    mappings.Base.metadata.create_all(engine)
    session = Session()
    get_indexer(_SEARCH, session)

    if dump is None:
        return engine

    people = ["Stuart", "Tarek"]
    qa_groups = []
    dbver = mappings.DatabaseVersion()
    dbver.version = DATABASE_VERSION
    session.add(dbver)

    def _find_user(firstname):
        p = mappings.User
        q = session.query(p).filter(p.firstname == firstname)
        return q.first()

    def _find_qa_group(name):
        g = mappings.Group
        q = session.query(g).filter(g.name == name)
        return q.first()

    # importing two editors
    stuart = mappings.User(firstname='Stuart', lastname='Philp',
                           github='stuartphilp', mozqa=True,
                           editor=True)

    tarek = mappings.User(firstname='Tarek', lastname='Ziade',
                          github='tarekziade', mozqa=True,
                          editor=True, email='tarek@mozilla.com')
    session.add(stuart)
    session.add(tarek)
    session.commit()

    # some langs
    langs = (('Python', '2.7'), ('Python', '3.5'), ('Javascript', None))

    for lang, ver in langs:
        plang = mappings.Language()
        plang.name = lang
        plang.version = ver
        session.add(plang)

    # some tags
    tags = 'ui', 'flask', 'node', 'experimental'

    for tag in tags:
        ptag = mappings.Tag()
        ptag.name = tag
        session.add(ptag)

    session.commit()

    def _random(table, size=2):
        items = session.query(table).all()
        choice = []
        while len(choice) < size:
            item = random.choice(items)
            if item not in choice:
                choice.append(item)
        return choice

    # importing people first
    for project in dump:
        # People
        for ppl in ('qa_primary', 'qa_secondary'):
            pid = project[ppl]['firstname']
            if pid in people:
                continue

            new = dict(project[ppl])
            new['mozqa'] = True
            if 'id' in new:
                del new['id']
            session.add(mappings.User(**new))
            people.append(pid)

        session.commit()

    for project in dump:
        print('Importing %s' % project['name'])
        # Groups
        qa_group_name = project['qa_group_name']
        if qa_group_name not in qa_groups:
            home = project['qa_group']['home']
            lead = _find_user(project['qa_group']['lead']['firstname'])
            session.add(mappings.Group(qa_group_name, home, lead))
            qa_groups.append(qa_group_name)

        session.commit()

        # The project itself
        proj = mappings.Project()
        proj.name = project['name']
        proj.description = project['description']
        proj.qa_primary = _find_user(project['qa_primary']['firstname'])
        proj.qa_secondary = _find_user(project['qa_secondary']['firstname'])
        proj.irc = project['irc']
        proj.qa_group = _find_qa_group(project['qa_group_name'])
        proj.public = True

        for deplo in project['deployments']:
            d = mappings.Deployment()
            d.name = deplo['name']
            d.endpoint = deplo['endpoint']
            d.public = True
            session.add(d)
            proj.deployments.append(d)

        # for each project we want
        tests = ['Test Suite', 'Unit', 'Functional/UI', 'Load',
                 'Performance', 'Accessibility', 'Security',
                 'Localization']

        for test in tests:
            ptest = mappings.ProjectTest()
            ptest.name = test
            ptest.url = 'http://example.org'
            ptest.operational = random.choice([True, False])
            ptest.jenkins_pipeline = False
            ptest.public = True
            proj.tests.append(ptest)

        proj.languages = _random(mappings.Language, 2)
        proj.tags = _random(mappings.Tag, 3)
        proj.bz_product = project['bz_component']
        proj.bz_component = project['bz_product']

        session.add(proj)
        session.commit()

    session.close()
    return engine


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description='ServiceBook Data importer.')

    parser.add_argument('--dump-file', help='Dump file',
                        type=str, default=_DUMP)

    parser.add_argument('--sqluri', help='Database',
                        type=str, default=_SQLURI)

    args = parser.parse_args(args=args)

    with open(args.dump_file) as f:
        dump = json.loads(f.read())

    init(sqluri=args.sqluri, dump=dump)
