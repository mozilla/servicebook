import os

from flask import Flask
from flask_bootstrap import Bootstrap

from servicebook.db import init
from servicebook import frontend, api, actions
from servicebook.nav import nav

HERE = os.path.dirname(__file__)


def create_app(fill=False, sqluri='sqlite:////tmp/qa_projects.db'):
    app = Flask(__name__, static_url_path='/static')
    Bootstrap(app)
    app.db = init(sqluri, fill)

    for bp in (frontend.frontend, api.api, actions.actions):
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
