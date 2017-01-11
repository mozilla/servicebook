# encoding: utf8
import time
from sqlalchemy_utils import URLType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Table
from sqlalchemy import Integer, Unicode, ForeignKey, UnicodeText, Boolean
from sqlalchemy.orm import relationship


published = []


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


def _now():
    return int(time.time() * 100)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(Unicode(128), nullable=False)
    lastname = Column(Unicode(128), nullable=False)
    mozqa = Column(Boolean, default=False)
    github = Column(Unicode(128))
    editor = Column(Boolean, default=False)
    email = Column(Unicode(128))
    last_modified = Column(Integer, nullable=False, default=_now)

    def __init__(self, firstname=None, lastname=None, github=None,
                 editor=False, mozqa=False, email=None):
        super(User, self).__init__()
        self.firstname = firstname
        self.lastname = lastname
        self.github = github
        self.editor = editor
        self.mozqa = mozqa
        self.email = email

    def __repr__(self):
        return '%s %s' % (self.firstname, self.lastname)

    def fullname(self):
        return self.__repr__()


published.append(User)


class Group(Base):
    __tablename__ = 'group'
    name = Column(Unicode(128), primary_key=True)
    home = Column(URLType())
    lead_id = Column(Integer, ForeignKey('user.id'))
    lead = relationship('User', foreign_keys='Group.lead_id')
    last_modified = Column(Integer, nullable=False, default=_now)

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


published.append(Group)


class Deployment(Base):
    __tablename__ = 'deployment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    endpoint = Column(URLType(), nullable=False)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates="deployments")
    last_modified = Column(Integer, nullable=False, default=_now)


published.append(Deployment)


class ProjectTest(Base):
    __tablename__ = 'project_test'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    url = Column(URLType())
    last_modified = Column(Integer, nullable=False, default=_now)
    operational = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates="tests")


published.append(ProjectTest)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    last_modified = Column(Integer, nullable=False, default=_now)


published.append(Tag)


project_tags = Table('project_tags', Base.metadata,
                     Column('project_id', Integer, ForeignKey('project.id')),
                     Column('tag_id', Integer, ForeignKey('tag.id')))


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    bz_product = Column(Unicode(128))
    bz_component = Column(Unicode(128))
    description = Column(UnicodeText)
    irc = Column(Unicode(128))

    # all project links
    homepage = Column(URLType())
    repository = Column(URLType())

    tags = relationship('Tag', secondary=project_tags)

    # all tests
    tests = relationship('ProjectTest', back_populates="project")

    # dev folks
    dev_primary_id = Column(Integer, ForeignKey('user.id'))
    dev_primary = relationship('User', foreign_keys='Project.dev_primary_id')
    dev_secondary_id = Column(Integer, ForeignKey('user.id'))
    dev_secondary = relationship('User',
                                 foreign_keys='Project.dev_secondary_id')

    # ops folks
    op_primary_id = Column(Integer, ForeignKey('user.id'))
    op_primary = relationship('User', foreign_keys='Project.op_primary_id')
    op_secondary_id = Column(Integer, ForeignKey('user.id'))
    op_secondary = relationship('User', foreign_keys='Project.op_secondary_id')

    # qa folks
    qa_primary_id = Column(Integer, ForeignKey('user.id'))
    qa_primary = relationship('User', foreign_keys='Project.qa_primary_id')
    qa_secondary_id = Column(Integer, ForeignKey('user.id'))
    qa_secondary = relationship('User', foreign_keys='Project.qa_secondary_id')
    qa_group_name = Column(Unicode(128), ForeignKey('group.name'))
    qa_group = relationship('Group', foreign_keys='Project.qa_group_name')

    deployments = relationship('Deployment', back_populates="project")
    last_modified = Column(Integer, nullable=False, default=_now)

    def __repr__(self):
        return '%s' % self.name

    def to_json(self):
        res = super(Project, self).to_json()
        res['deployments'] = [depl.to_json() for depl in self.deployments]
        res['tests'] = [test.to_json() for test in self.tests]
        for field in ('qa_primary', 'qa_secondary', 'dev_primary',
                      'dev_secondary', 'ops_primary', 'ops_secondary'):
            user = getattr(self, field, None)
            if user is not None:
                res[field] = user.to_json()
        res['qa_group'] = self.qa_group.to_json()
        res['tags'] = [tag.to_json() for tag in self.tags]
        return res


published.append(Project)
