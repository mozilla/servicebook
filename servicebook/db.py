# encoding: utf8
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine

import mappings


session_factory = sessionmaker(autoflush=False)
Session = scoped_session(session_factory)


_PEOPLE = """\
Stuart Philp
Krupa Raj
Dave Hunt
Richard Pappalardo
Karl Thiessen
Peter deHaan
Chris Hartjes
Stephen Donner
Kevin Brosnan
Aaron Train
Matt Brandt
Rebecca Billings
John Dorlus
No-Jun Park
Benny Forehand Jr.
"""

_GROUPS = [
("User Interfaces", "https://wiki.mozilla.org/TestEngineering/UI", "Dave Hunt"),
("Services", "https://wiki.mozilla.org/TestEngineering/Services", "Richard Pappalardo"),
("Customization", "https://wiki.mozilla.org/TestEngineering/Customization", "Krupa Raj"),
]

_PROJS = [
["Shavar (Tracking Protection)", "Rebecca", "Richard", "#shavar", "Services"],
["ABSearch", "Karl", "Chris", "#absearch", "Services"],
["Balrog", "Chris", "Karl", "#balrog", "Services"]

]



def init(sqluri='sqlite:////tmp/qa_projects.db', fill=False):
    engine = create_engine(sqluri)
    session_factory.configure(bind=engine)
    mappings.Base.metadata.create_all(engine)
    if not fill:
        return engine

    session = Session()

    for person in _PEOPLE.split('\n'):
        if person.strip() == '':
            continue
        first, last = person.split(' ', 1)
        session.add(mappings.Person(first, last))

    session.commit()

    p = mappings.Person
    g = mappings.Group

    def _find_person(firstname):
        q = session.query(p).filter(p.firstname==firstname)
        return q.first()


    def _find_group(name):
        q = session.query(g).filter(g.name==name)
        return q.first()

    for label, home, lead in _GROUPS:
        lead = session.query(p).filter(p.lastname==lead.split(' ', 1)[-1])
        session.add(mappings.Group(label, home, lead.first()))

    session.commit()

    for project in _PROJS:
        proj = mappings.Project()
        proj.name = project[0]
        proj.primary = _find_person(project[1])
        proj.secondary = _find_person(project[2])
        proj.irc = project[3]
        proj.group = _find_group(project[4]).name
        session.add(proj)

    session.commit()
    session.close()
    return engine


if __name__ == '__main__':
    init(fill=True)
