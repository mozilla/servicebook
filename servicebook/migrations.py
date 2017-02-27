""" Place holder to programmatically change the DB.
"""
from servicebook import mappings


def increment_database(engine, session, current):

    if current == 0:
        # public flag
        public = 'alter table %s add column public BOOLEAN DEFAULT True'
        for table in ('project', 'deployment', 'project_test', 'jenkins_job',
                      'testrail', 'link'):
            engine.execute(public % table)

        # jenkins_pipeline in project_test
        sql = ('alter table project_test add column jenkins_pipeline BOOLEAN '
               'DEFAULT False')
        engine.execute(sql)

        # adding new tables
        mappings.DatabaseVersion.__table__.create(bind=engine, checkfirst=True)

    return current + 1
