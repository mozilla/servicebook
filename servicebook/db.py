# encoding: utf8
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

from servicebook import mappings
from servicebook.data import PEOPLE, GROUPS, PROJS


session_factory = sessionmaker(autoflush=False)
Session = scoped_session(session_factory)


def init(sqluri='sqlite:////tmp/qa_projects.db', fill=False):
    engine = create_engine(sqluri)
    session_factory.configure(bind=engine)
    mappings.Base.metadata.create_all(engine)
    if not fill:
        return engine

    session = Session()

    for person in PEOPLE.split('\n'):
        if person.strip() == '':
            continue
        first, last = person.split(' ', 1)
        session.add(mappings.Person(first, last))

    session.commit()

    p = mappings.Person
    g = mappings.Group

    def _find_person(firstname):
        q = session.query(p).filter(p.firstname == firstname)
        return q.first()

    def _find_group(name):
        q = session.query(g).filter(g.name == name)
        return q.first()

    for label, home, lead in GROUPS:
        lead = session.query(p).filter(p.lastname == lead.split(' ', 1)[-1])
        session.add(mappings.Group(label, home, lead.first()))

    session.commit()

    for project in PROJS:
        proj = mappings.Project()
        proj.name = project[0]
        print('Importing %s' % proj.name)
        proj.description = project[1]
        proj.primary = _find_person(project[2])
        proj.secondary = _find_person(project[3])
        proj.irc = project[4]
        proj.group = _find_group(project[5]).name
        for deplo in project[6]:
            d = mappings.Deployment()
            d.name = deplo[0]
            d.endpoint = deplo[1]
            session.add(d)
            proj.deployments.append(d)

        if project[7] != []:
            proj.bz_product = project[7][0]
            proj.bz_component = project[7][1]

        session.add(proj)

    session.commit()
    session.close()
    return engine


def main():
    init(fill=True)
