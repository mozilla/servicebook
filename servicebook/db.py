# encoding: utf8
import os
import json
import argparse
import sys

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from servicebook import mappings


session_factory = sessionmaker(autoflush=False)
Session = scoped_session(session_factory)
here = os.path.dirname(__file__)
_DUMP = os.path.join(here, 'dump.json')
_SQLURI = 'sqlite:////tmp/qa_projects.db'


def init(sqluri=_SQLURI, dump=None):
    engine = create_engine(sqluri)
    session_factory.configure(bind=engine)
    mappings.Base.metadata.create_all(engine)

    if dump is None:
        return engine

    session = Session()

    people = ["Stuart", "Tarek"]
    qa_groups = []

    def _find_user(firstname):
        p = mappings.User
        q = session.query(p).filter(p.firstname == firstname)
        return q.first()

    def _find_qa_group(name):
        g = mappings.Group
        q = session.query(g).filter(g.name == name)
        return q.first()

    # importing two editors
    stuart = mappings.User('Stuart', 'Philp', 'stuartphilp', True, True)
    tarek = mappings.User('Tarek', 'Ziade', 'tarekziade', True, True,
                          'tarek@mozilla.com')
    session.add(stuart)
    session.add(tarek)
    session.commit()

    # importing people first
    for project in dump:
        # People
        for ppl in ('qa_primary', 'qa_secondary'):
            pid = project[ppl]['firstname']
            if pid in people:
                continue
            firstname = project[ppl]['firstname']
            lastname = project[ppl]['lastname']
            github = project[ppl].get('github')
            editor = project[ppl].get('editor', False)
            mozqa = True
            session.add(mappings.User(firstname, lastname, github, editor,
                                      mozqa))
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

        for deplo in project['deployments']:
            d = mappings.Deployment()
            d.name = deplo['name']
            d.endpoint = deplo['endpoint']
            session.add(d)
            proj.deployments.append(d)

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
