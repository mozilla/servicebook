# encoding: utf8
import os
import json
import argparse
import sys

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
DATABASE_VERSION = 3


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
    session.bind = engine

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

    people = []
    qa_groups = []

    dbver = mappings.DatabaseVersion()
    dbver.version = DATABASE_VERSION
    session.add(dbver)

    def _find_entry(mapping, field, value):
        f = getattr(mapping, field)
        q = session.query(mapping).filter(f == value)
        return q.first()

    def _find_user(firstname):
        return _find_entry(mappings.User, 'firstname', firstname)

    def _find_qa_group(name):
        return _find_entry(mappings.Group, 'name', name)

    # predefined teams
    for team in ('Dev', 'QA', 'OPS'):
        t = mappings.Team(name=team)
        session.add(t)
    session.commit()

    # importing people first
    for project in dump['data']:
        # People
        for ppl in ('qa_primary', 'qa_secondary', 'dev_primary',
                    'dev_secondary',
                    'op_primary', 'op_secondary'):
            person = project.get(ppl)
            if person is None:
                continue
            pid = person['firstname']
            if pid in people:
                continue
            new = dict(project[ppl])
            if 'id' in new:
                del new['id']
            teams = {}
            for team in ('team', 'secondary_team'):
                if team not in new:
                    continue
                team_data = new[team]
                entry = _find_entry(mappings.Team, 'name', team_data['name'])
                if entry is None:
                    del team_data['id']
                    print('Creating team ' + team_data['name'])
                    t = mappings.Team(**team_data)
                    session.add(t)
                    session.commit()
                    teams[team_data['name']] = t
                    new[team + '_id'] = t.id
                else:
                    new[team + '_id'] = entry.id

                del new[team]

            user = mappings.User(**new)
            print('Created user ' + str(user))
            session.add(user)
            people.append(pid)
        session.commit()

    for project in dump['data']:
        print('Importing %s' % project['name'])
        project = dict(project)
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
        proj.from_json(project)
        for role in ('qa_primary', 'qa_secondary', 'dev_primary',
                     'dev_secondary',
                     'op_primary', 'op_secondary'):
            if role not in project:
                continue
            setattr(proj, role, _find_user(project[role]['firstname']))

        proj.qa_group = _find_qa_group(project['qa_group_name'])

        rels = (('tests', mappings.ProjectTest, None),
                ('repositories', mappings.Link, 'url'),
                ('tags', mappings.Tag, 'name'),
                ('languages', mappings.Language, 'name'),
                ('testrail', mappings.TestRail, None),
                ('jenkins_jobs', mappings.JenkinsJob, None),
                ('deployments', mappings.Deployment, None))

        for attr, mapping, dupe in rels:
            for item in project[attr]:
                item = dict(item)
                if dupe is not None:
                    e = _find_entry(mapping, dupe, item[dupe])
                    if e:
                        getattr(proj, attr).append(e)
                        continue

                if 'id' in item:
                    del item['id']
                ob = mapping(**item)
                session.add(ob)
                getattr(proj, attr).append(ob)

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
