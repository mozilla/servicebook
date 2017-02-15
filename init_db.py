import os
from servicebook.db import main


sqluri = os.environ.get('SQLURI')

if sqluri is not None and sqluri.startswith('sqlite:///'):
    filename = sqluri.split('sqlite:///')[-1]
    if not os.path.exists(filename):
        main(['--sqluri', sqluri])
