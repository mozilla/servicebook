# encoding: utf8
import uuid
import time
from sqlalchemy_utils import URLType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Table
from sqlalchemy import (Integer, Unicode, ForeignKey, UnicodeText, Boolean,
                        BigInteger)
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

    def index(self):
        return ''


def _now():
    return int(time.time() * 1000)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    firstname = Column(Unicode(128), nullable=False)
    lastname = Column(Unicode(128), nullable=False)
    irc = Column(Unicode(128))
    mozillians_login = Column(Unicode(128))
    mozqa = Column(Boolean, default=False)
    github = Column(Unicode(128))
    editor = Column(Boolean, default=False)
    email = Column(Unicode(128))
    last_modified = Column(BigInteger, nullable=False, default=_now)

    def __init__(self, **kw):
        super(User, self).__init__()
        for key, val in kw.items():
            if hasattr(self, key):
                setattr(self, key, val)

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
    last_modified = Column(BigInteger, nullable=False, default=_now)

    def __init__(self, name=None, home=None, lead=None):
        super(Group, self).__init__()
        self.name = name
        self.home = home
        self.lead = lead

    def __repr__(self):
        return self.name

    def to_json(self):
        res = super(Group, self).to_json()
        if self.lead:
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
    last_modified = Column(BigInteger, nullable=False, default=_now)


published.append(Deployment)


class ProjectTest(Base):
    __tablename__ = 'project_test'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    url = Column(URLType())
    last_modified = Column(BigInteger, nullable=False, default=_now)
    operational = Column(Boolean, default=False)
    jenkins_pipeline = Column(Boolean, default=False)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates="tests")


published.append(ProjectTest)


class JenkinsJob(Base):
    __tablename__ = 'jenkins_job'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    jenkins_server = Column(URLType())
    last_modified = Column(BigInteger, nullable=False, default=_now)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates="jenkins_jobs")


published.append(JenkinsJob)


class TestRail(Base):
    __tablename__ = 'testrail'
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, nullable=False)
    test_rail_server = Column(URLType())
    last_modified = Column(BigInteger, nullable=False, default=_now)
    project_id = Column(Integer, ForeignKey('project.id'))
    project = relationship('Project', back_populates="testrail")


published.append(TestRail)


class Language(Base):
    __tablename__ = 'language'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    version = Column(Unicode(128))
    last_modified = Column(BigInteger, nullable=False, default=_now)

    def __str__(self):
        if self.version is None:
            return self.name
        return '%s %s' % (self.name, self.version)


project_langs = Table('project_langs', Base.metadata,
                      Column('project_id', Integer, ForeignKey('project.id')),
                      Column('language_id', Integer,
                             ForeignKey('language.id')))


published.append(Language)


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    last_modified = Column(BigInteger, nullable=False, default=_now)


project_tags = Table('project_tags', Base.metadata,
                     Column('project_id', Integer, ForeignKey('project.id')),
                     Column('tag_id', Integer, ForeignKey('tag.id')))

published.append(Tag)


class Link(Base):
    __tablename__ = 'link'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(URLType(), nullable=False)
    name = Column(Unicode(128))
    last_modified = Column(BigInteger, nullable=False, default=_now)


project_repos = Table('project_repos', Base.metadata,
                      Column('project_id', Integer, ForeignKey('project.id')),
                      Column('link_id', Integer, ForeignKey('link.id')))


published.append(Link)


class Project(Base):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Unicode(128), nullable=False)
    bz_product = Column(Unicode(128))
    bz_component = Column(Unicode(128))
    description = Column(UnicodeText)
    long_description = Column(UnicodeText)
    irc = Column(Unicode(128))

    # all project links
    homepage = Column(URLType())
    repositories = relationship('Link', secondary=project_repos)
    tags = relationship('Tag', secondary=project_tags)
    languages = relationship('Language', secondary=project_langs)
    testrail = relationship('TestRail', back_populates="project")

    # all tests
    tests = relationship('ProjectTest', back_populates="project")
    jenkins_jobs = relationship('JenkinsJob', back_populates="project")

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
    last_modified = Column(BigInteger, nullable=False, default=_now)

    def __repr__(self):
        return '%s' % self.name

    def to_json(self):
        res = super(Project, self).to_json()
        res['deployments'] = [depl.to_json() for depl in self.deployments]
        res['tests'] = [test.to_json() for test in self.tests]
        res['jenkins_jobs'] = [job.to_json() for job in self.jenkins_jobs]
        res['testrail'] = [tr.to_json() for tr in self.testrail]

        for field in ('qa_primary', 'qa_secondary', 'dev_primary',
                      'dev_secondary', 'op_primary', 'op_secondary'):
            user = getattr(self, field, None)
            if user is not None:
                res[field] = user.to_json()
        res['qa_group'] = self.qa_group.to_json()
        for rel in ('tags', 'languages', 'repositories'):
            res[rel] = [item.to_json() for item in getattr(self, rel)]
        return res

    def index(self):
        res = self.name
        res += ' ' + ' '.join([tag.name for tag in self.tags])
        res += ' ' + ' '.join([str(lang) for lang in self.languages])
        if self.long_description:
            res += ' ' + self.long_description
        if self.description:
            res += ' ' + self.description
        if self.irc:
            res += ' ' + self.irc

        for user in (self.dev_primary, self.dev_secondary,
                     self.op_primary, self.op_secondary,
                     self.qa_primary, self.qa_secondary):
            if user is not None:
                res += ' ' + user.fullname()

        if self.qa_group_name:
            res += ' ' + self.qa_group_name

        return res


published.append(Project)


class AuthenticationKey(Base):
    __tablename__ = 'keys'
    id = Column(Integer, primary_key=True, autoincrement=True)
    application = Column(Unicode(128), nullable=False)
    key = Column(Unicode(128), nullable=False)
    last_modified = Column(BigInteger, nullable=False, default=_now)

    def __init__(self, application, key=None):
        super(AuthenticationKey, self).__init__()
        self.application = application
        if key is None:
            key = str(uuid.uuid4())
        self.key = key

    def __str__(self):
        return 'App: %s, Key: %s' % (self.application, self.key)
