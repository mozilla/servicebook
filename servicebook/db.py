# encoding: utf8
import os
import json

from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from servicebook import mappings


session_factory = sessionmaker(autoflush=False)
Session = scoped_session(session_factory)


def init(sqluri='sqlite:////tmp/qa_projects.db', dump=None):
    engine = create_engine(sqluri)
    session_factory.configure(bind=engine)
    mappings.Base.metadata.create_all(engine)

    if dump is None:
        return engine

    session = Session()

    people = []
    groups = []

    def _find_person(firstname):
        p = mappings.Person
        q = session.query(p).filter(p.firstname == firstname)
        return q.first()

    def _find_group(name):
        g = mappings.Group
        q = session.query(g).filter(g.name == name)
        return q.first()

    # importing people first
    for project in dump:
        # People
        for ppl in ('primary', 'secondary'):
            pid = project[ppl]['id']
            if pid in people:
                continue
            firstname = project[ppl]['firstname']
            lastname = project[ppl]['lastname']
            session.add(mappings.Person(firstname, lastname))
            people.append(pid)

        session.commit()

    for project in dump:
        print('Importing %s' % project['name'])
        # Groups
        group_name = project['group_name']
        if group_name not in groups:
            home = project['group']['home']
            lead = _find_person(project['group']['lead']['firstname'])
            session.add(mappings.Group(group_name, home, lead))
            groups.append(group_name)

        session.commit()

        # The project itself
        proj = mappings.Project()
        proj.name = project['name']
        proj.description = project['description']
        proj.primary = _find_person(project['primary']['firstname'])
        proj.secondary = _find_person(project['secondary']['firstname'])
        proj.irc = project['irc']
        proj.group = _find_group(project['group_name'])

        for deplo in project['deployments']:
            d = mappings.Deployment()
            d.name = deplo['name']
            d.endpoint = deplo['endpoint']
            session.add(d)
            proj.deployments.append(d)

        proj.bz_product = project['bz_component']
        proj.bz_component = project['bz_product']

        for link in project['links']:
            d = mappings.Link()
            d.name = link['name']
            d.description = link['description']
            d.link = link['link']
            session.add(d)
            proj.links.append(d)

        session.add(proj)
        session.commit()

    session.close()
    return engine


def main():
    here = os.path.dirname(__file__)
    with open(os.path.join(here, 'dump.json')) as f:
        dump = json.loads(f.read())

    init(dump=dump)
