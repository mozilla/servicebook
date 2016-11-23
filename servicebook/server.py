import json
import os

from flask import Flask, g
from flask_bootstrap import Bootstrap

from servicebook.db import init
from servicebook.nav import nav
from servicebook.views import frontend, api, actions, auth
from servicebook.auth import get_user


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

    for bp in (frontend.frontend, api.api, actions.actions, auth.auth):
        app.register_blueprint(bp)

    app.register_error_handler(401, auth.unauthorized_view)

    nav.init_app(app)

    app.add_url_rule(
           app.static_url_path + '/<path:filename>',
           endpoint='static',
           view_func=app.send_static_file)

    @app.before_request
    def before_req():
        g.user = get_user()

    return app


def main():
    app = create_app()
    app.run(debug=True)


if __name__ == "__main__":
    main()
