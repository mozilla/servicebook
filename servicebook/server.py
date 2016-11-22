import json
import os

from flask import Flask, session
from flask_bootstrap import Bootstrap

from servicebook.db import init
from servicebook.nav import nav


HERE = os.path.dirname(__file__)


def create_app(sqluri='sqlite:////tmp/qa_projects.db', dump=None):
    app = Flask(__name__, static_url_path='/static')
    app.secret_key = "we'll do better later"
    app.config['SESSION_TYPE'] = 'filesystem'

    Bootstrap(app)

    if dump is not None:
        with open(dump) as f:
            dump = json.loads(f.read())

    app.db = init(sqluri, dump)

    from servicebook.views import frontend, api, actions, auth

    for bp in (frontend.frontend, api.api, actions.actions, auth.auth):
        app.register_blueprint(bp)

    nav.init_app(app)

    app.add_url_rule(
           app.static_url_path + '/<path:filename>',
           endpoint='static',
           view_func=app.send_static_file)

    return app


def main():
    app = create_app()
    app.run(debug=True)


if __name__ == "__main__":
    main()
