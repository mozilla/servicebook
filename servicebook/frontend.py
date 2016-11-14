from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_nav import Nav
from flask import Blueprint

from db import init, Session
import mappings
from nav import nav


frontend = Blueprint('frontend', __name__)

nav.register_element('frontend_top', Navbar(
        View('Home', '.home'),
))


@frontend.route("/")
def home():
    projects = Session.query(mappings.Project)
    return render_template('home.html', projects=projects)



