import json
import os
import logging.config

from flask import Flask, g
from flask.ext.iniconfig import INIConfig
from flask.ext.restless import APIManager

from servicebook.db import init, Session
from servicebook.auth import get_user, GithubAuth, raise_if_not_editor
from servicebook.mappings import published


HERE = os.path.dirname(__file__)
DEFAULT_INI_FILE = os.path.join(HERE, '..', 'servicebook.ini')
_DEBUG = True


def create_app(ini_file=DEFAULT_INI_FILE, dump=None):
    app = Flask(__name__)
    INIConfig(app)
    app.config.from_inifile(ini_file)
    app.secret_key = app.config['common']['secret_key']
    sqluri = app.config['common']['sqluri']

    GithubAuth(app)

    if dump is not None:
        with open(dump) as f:
            dump = json.loads(f.read())

    app.db = init(sqluri, dump)

    preprocessors = {'POST': [raise_if_not_editor],
                     'DELETE': [raise_if_not_editor],
                     'PUT': [raise_if_not_editor]}

    manager = APIManager(app, flask_sqlalchemy_db=app.db,
                         session=Session(),
                         preprocessors=preprocessors)

    def to_json(instance):
        return instance.to_json()

    for model in published:
        manager.create_api(model, methods=['GET', 'POST', 'DELETE'],
                           serializer=to_json)

    @app.before_request
    def before_req():
        g.user = get_user(app)
        g.debug = _DEBUG

    logging.config.fileConfig(ini_file)
    return app


def main():
    app = create_app()
    app.run(debug=_DEBUG, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()
