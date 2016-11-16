import os

from flask import Flask
from flask_bootstrap import Bootstrap

from servicebook.db import init
from servicebook import frontend
from servicebook.nav import nav

HERE = os.path.dirname(__file__)


def create_app():
    app = Flask(__name__, static_url_path='/static')
    Bootstrap(app)
    app.db = init()
    app.register_blueprint(frontend.frontend)
    nav.init_app(app)

    app.add_url_rule(
           app.static_url_path + '/<path:filename>',
           endpoint='static',
           view_func=app.send_static_file)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
