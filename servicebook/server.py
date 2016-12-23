import os
import logging.config
import sys
import argparse
import time

from flask import Flask, g
from flask.ext.iniconfig import INIConfig
from flask_restless_swagger import SwagAPIManager as APIManager

from servicebook.db import init, Session
from servicebook.mappings import published


HERE = os.path.dirname(__file__)
DEFAULT_INI_FILE = os.path.join(HERE, '..', 'servicebook.ini')
_DEBUG = True


def add_timestamp(*args, **kw):
    kw['data']['last_modified'] = int(time.time() * 1000)


def create_app(ini_file=DEFAULT_INI_FILE):
    app = Flask(__name__)
    INIConfig(app)
    app.config.from_inifile(ini_file)
    app.secret_key = app.config['common']['secret_key']
    sqluri = app.config['common']['sqluri']
    app.db = init(sqluri)

    preprocessors = {}
    for method in ('POST', 'PATCH_SINGLE', 'PUT_SINGLE', 'PATCH_MANY',
                   'PUT_MANY', 'DELETE_SINGLE', 'DELETE_MANY'):
        preprocessors[method] = [add_timestamp]

    manager = APIManager(app, flask_sqlalchemy_db=app.db,
                         session=Session(),
                         preprocessors=preprocessors)

    def to_json(instance):
        return instance.to_json()

    methods = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']

    for model in published:
        manager.create_api(model, methods=methods, serializer=to_json,
                           results_per_page=50)

    @app.before_request
    def before_req():
        g.debug = _DEBUG

    logging.config.fileConfig(ini_file)
    return app


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='ServiceBook Server.')

    parser.add_argument('--config-file', help='Config file',
                        type=str, default=DEFAULT_INI_FILE)
    parser.add_argument(
        '--no-run', action='store_true', default=False)

    args = parser.parse_args(args=args)
    app = create_app(ini_file=args.config_file)
    host = app.config['common'].get('host', '0.0.0.0')
    port = app.config['common'].get('port', 5001)
    debug = app.config.get('DEBUG', _DEBUG)

    if args.no_run:
        return app

    app.run(debug=debug, host=host, port=port)


if __name__ == "__main__":
    main()
