import site
import sys
import os
import codecs
from servicebook.server import create_app


ini = os.path.join(os.path.dirname(__file__), 'servicebook.ini')
application = create_app(ini_file=ini)


if __name__ == "__main__":
    application.run(host='0.0.0.0')
