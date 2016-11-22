# encoding: utf8
from sqlalchemy_utils import URLType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer, Unicode, ForeignKey, UnicodeText, Boolean
from sqlalchemy.orm import relationship


def _declarative_base(cls):
    return declarative_base(cls=cls)


@_declarative_base
class Base(object):
    @property
    def columns(self):
        return [col.name for col in self.__table__.columns]

    def to_json(self):
        res = {}
        for col in self.columns:
            res[col] = getattr(self, col)
        return res


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(Unicode(128), nullable=False)
    lastname = Column(Unicode(128), nullable=False)
    mozqa = Column(Boolean, default=False)
    github = Column(Unicode(128))
    editor = Column(Boolean, default=False)

    def __init__(self, firstname=None, lastname=None, github=None,
                 editor=False, mozqa=False):
        super(Person, self).__init__()
        self.firstname = firstname
        self.lastname = lastname
        self.github = github
        self.editor = editor
        self.mozqa = mozqa

    def __repr__(self):
        return '%s %s' % (self.firstname, self.lastname)

    def fullname(self):
        return self.__repr__()


class Group(Base):
    __tablename__ = 'group'
    name = Column(Unicode(128), primary_key=True)
    home = Column(URLType())
    lead_id = Column(Integer, ForeignKey('person.id'))
    lead = relationship('Person', foreign_keys='Group.lead_id')

    def __init__(self, name=None, home=None, lead=None):
        super(Group, self).__init__()
        self.name = name
        self.home = home
        self.lead = lead

    def __repr__(self):
        return self.name

    def to_json(self):
        res = super(Group, self).to_json()
        res['lead'] = self.lead.to_json()
        return res


class Deployment(Base):
    __tablename__ = 'deployment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    endpoint = Column(URLType(), nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates="deployments")


class Link(Base):
    __tablename__ = 'link'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    description = Column(UnicodeText)
    link = Column(URLType(), nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates="links")


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    bz_product = Column(Unicode(128))
    bz_component = Column(Unicode(128))
    description = Column(UnicodeText)
    primary_id = Column(Integer, ForeignKey('person.id'))
    primary = relationship('Person', foreign_keys='Project.primary_id')
    secondary_id = Column(Integer, ForeignKey('person.id'))
    secondary = relationship('Person', foreign_keys='Project.secondary_id')
    irc = Column(Unicode(128))
    group_name = Column(Unicode(128), ForeignKey('group.name'))
    group = relationship('Group', foreign_keys='Project.group_name')

    deployments = relationship('Deployment', back_populates="project")
    links = relationship('Link', back_populates="project")

    def __repr__(self):
        return '%s' % self.name

    def to_json(self):
        res = super(Project, self).to_json()
        res['deployments'] = [depl.to_json() for depl in self.deployments]
        res['links'] = [link.to_json() for link in self.links]
        res['primary'] = self.primary.to_json()
        res['secondary'] = self.secondary.to_json()
        res['group'] = self.group.to_json()
        return res
