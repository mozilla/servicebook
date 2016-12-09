import json
import os
import logging.config

from flask import Flask, g
from flask_bootstrap import Bootstrap
from flask.ext.iniconfig import INIConfig

from servicebook.db import init
from servicebook.nav import nav
from servicebook.views import blueprints
from servicebook.auth import get_user, GithubAuth
from servicebook.views.auth import unauthorized_view
from servicebook.mozillians import Mozillians
from servicebook.translations import APP_TRANSLATIONS


HERE = os.path.dirname(__file__)
DEFAULT_INI_FILE = os.path.join(HERE, '..', 'servicebook.ini')
_DEBUG = True


def create_app(ini_file=DEFAULT_INI_FILE, dump=None):
    app = Flask(__name__, static_url_path='/static')
    INIConfig(app)
    app.config.from_inifile(ini_file)
    app.secret_key = app.config['common']['secret_key']
    sqluri = app.config['common']['sqluri']

    Bootstrap(app)
    GithubAuth(app)
    Mozillians(app)

    if dump is not None:
        with open(dump) as f:
            dump = json.loads(f.read())

    app.db = init(sqluri, dump)

    for bp in blueprints:
        app.register_blueprint(bp)
        bp.app = app

    app.register_error_handler(401, unauthorized_view)
    nav.init_app(app)

    app.add_url_rule(
           app.static_url_path + '/<path:filename>',
           endpoint='static',
           view_func=app.send_static_file)

    @app.before_request
    def before_req():
        g.user = get_user(app)
        g.debug = _DEBUG

    @app.template_filter('translate')
    def translate_string(s):
        return APP_TRANSLATIONS.get(s, s)

    @app.template_filter('capitalize')
    def capitalize_string(s):
        return s[0].capitalize() + s[1:]

    logging.config.fileConfig(ini_file)
    return app


def main():
    app = create_app()
    app.run(debug=_DEBUG, host='0.0.0.0', port=5000)


if __name__ == "__main__":
    main()
