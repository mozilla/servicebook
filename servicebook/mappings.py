# encoding: utf8
from sqlalchemy_utils import ScalarListType, URLType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Unicode, ForeignKey


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
        self.id = None


class Group(Base):
    __tablename__ = 'group'
    name = Column(Unicode(128), primary_key=True)
    home = Column(URLType())
    lead = Column(Integer, ForeignKey('person.id'))

    def __init__(self, name=None, home=None, lead=None):
        super(Group, self).__init__()
        self.name = name
        self.home = home
        if lead is not None:
            self.lead = lead.id
        else:
            self.lead = lead


class Project(Base):
    __tablename__ = 'project'
    name = Column(Unicode(128), primary_key=True)
    primary = Column(Integer, ForeignKey('person.id'))
    secondary = Column(Integer, ForeignKey('person.id'))
    irc = Column(Unicode(128))
    group = Column(Unicode(128), ForeignKey('group.name'))

    swagger_def = Column(URLType())
    test_suite = Column(ScalarListType(URLType))
    unit_tests = Column(ScalarListType(URLType))
    functional_tests = Column(ScalarListType(URLType))
    load_tests = Column(ScalarListType(URLType))
    perf_tests = Column(ScalarListType(URLType))
    accessibility_tests = Column(ScalarListType(URLType))
    sec_tests = Column(ScalarListType(URLType))
    localization_tests = Column(ScalarListType(URLType))
