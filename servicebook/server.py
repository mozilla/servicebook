import os
from flask import Flask, render_template, send_from_directory
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_nav import Nav
from flask import Blueprint

from db import init, Session
import mappings
import frontend
from nav import nav

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
