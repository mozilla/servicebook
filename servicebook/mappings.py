# encoding: utf8
from sqlalchemy_utils import ScalarListType, URLType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, ForeignKey, UnicodeText
from sqlalchemy.orm import relationship


Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(Unicode(128))
    lastname = Column(Unicode(128))

    def __init__(self, firstname=None, lastname=None):
        super(Person, self).__init__()
        self.firstname = firstname
        self.lastname = lastname

    def __repr__(self):
        return '%s %s' % (self.firstname, self.lastname)


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


class Deployment(Base):
    __tablename__ = 'deployment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128))
    endpoint = Column(URLType())
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates="deployments")


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128))
    bz_product = Column(Unicode(128))
    bz_component = Column(Unicode(128))
    description = Column(UnicodeText)
    primary_id = Column(Integer, ForeignKey('person.id'))
    primary = relationship('Person', foreign_keys='Project.primary_id')
    secondary_id = Column(Integer, ForeignKey('person.id'))
    secondary = relationship('Person', foreign_keys='Project.secondary_id')
    irc = Column(Unicode(128))
    group = Column(Unicode(128), ForeignKey('group.name'))

    deployments = relationship('Deployment', back_populates="project")

    test_suite = Column(ScalarListType(URLType))
    unit_tests = Column(ScalarListType(URLType))
    functional_tests = Column(ScalarListType(URLType))
    load_tests = Column(ScalarListType(URLType))
    perf_tests = Column(ScalarListType(URLType))
    accessibility_tests = Column(ScalarListType(URLType))
    sec_tests = Column(ScalarListType(URLType))
    localization_tests = Column(ScalarListType(URLType))
