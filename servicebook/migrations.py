""" Place holder to programmatically change the DB.
"""
from servicebook import mappings


def increment_database(engine, session, current):
    engine.echo = True

    if current == 0:
        # public flag
        public = 'alter table %s add column public BOOLEAN DEFAULT True;'
        for table in ('project', 'deployment', 'project_test', 'jenkins_job',
                      'testrail', 'link'):
            engine.execute(public % table)

        # jenkins_pipeline in project_test
        sql = ('alter table project_test add column jenkins_pipeline BOOLEAN '
               'DEFAULT False')
        engine.execute(sql)

        # adding new tables
        for table in (mappings.DatabaseVersion, mappings.Team):
            table.__table__.create(bind=engine, checkfirst=True)

        # adding teams
        for team_name in ('OPS', 'QA', 'Dev', 'Community'):
            team = mappings.Team(team_name)
            session.add(team)

        # re-creating table user (for the new team key)
        engine.execute('alter table user rename to old_user')
        mappings.User.__table__.create(bind=engine)
        fields = ['id', 'firstname', 'lastname', 'irc', 'mozillians_login',
                  'mozqa', 'github', 'editor', 'email', 'last_modified']
        fields = ','.join(fields)
        engine.execute('insert into user (%s) select * from old_user' %
                       (fields))
        engine.execute('drop table old_user')

    return current + 1
