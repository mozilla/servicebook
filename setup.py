from setuptools import setup, find_packages
from servicebook import __version__


setup(name='servicebook',
      version=__version__,
      packages=find_packages(),
      description="Mozilla QA Service Book",
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        'flask-iniconfig',
        'flask-restless-swagger',
        'flask-restless',
        'flask-sqlalchemy',
        'flask',
        'PyMySQL',
        'PyYAML',
        'raven[flask]',
        'requests',
        'SQLAlchemy-Utils',
        'SQLALchemy',
        'whoosh',
      ],
      entry_points="""
      [console_scripts]
      servicebook = servicebook.server:main
      servicebook-import = servicebook.db:main
      servicebook-reindex = servicebook.db:reindex
      servicebook-keys = servicebook.keys:main
      servicebook-migrate-db = servicebook.db:migrate_db
      """)
