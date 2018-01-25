""" Place holder to programmatically change the DB.
"""
from servicebook import mappings
from sqlalchemy.exc import OperationalError


def increment_database(engine, session, current):
    engine.echo = True

    if current == 0:
        # adding new tables
        for table in (mappings.DatabaseVersion, mappings.Team,
                      mappings.TestRail, mappings.AuthenticationKey):
            try:
                table.__table__.create(bind=engine)

            except OperationalError:
                pass

        # public flag
        public = 'alter table %s add column public BOOLEAN DEFAULT True;'
        for table in ('project', 'deployment', 'project_test', 'jenkins_job',
                      'testrail', 'link'):
            try:
                engine.execute(public % table)
            except OperationalError:
                if table != 'testrail':
                    raise

        # jenkins_pipeline in project_test
        sql = ('alter table project_test add column jenkins_pipeline BOOLEAN '
               'DEFAULT False')
        engine.execute(sql)

        # adding teams
        for team_name in ('OPS', 'QA', 'Dev', 'Community'):
            team = mappings.Team(team_name)
            session.add(team)
        session.commit()

        # re-creating table user (for the new team key)
        engine.execute('alter table user rename to old_user')
        mappings.User.__table__.create(bind=engine)
        fields = ['id', 'firstname', 'lastname', 'irc', 'mozillians_login',
                  'github', 'editor', 'email', 'last_modified']
        fields = ','.join(fields)
        engine.execute('insert into user (%s) select %s from old_user' %
                       (fields, fields))
        engine.execute('drop table old_user')
    elif current == 1:
        sql = ('alter table authkeys add column scope STRING '
               'DEFAULT "read"')
        try:
            engine.execute(sql)
        except OperationalError:
            pass
    elif current == 2:
        public = 'alter table user add column public BOOLEAN DEFAULT False;'
        try:
            engine.execute(public)
        except OperationalError:
            pass
        remove = 'alter table user add column mozqa'
        try:
            engine.execute(remove)
        except OperationalError:
            pass
    elif current == 3:
        active = 'alter table project add column active BOOLEAN DEFAULT True;'
        try:
            engine.execute(active)
        except OperationalError:
            pass
    return current + 1
