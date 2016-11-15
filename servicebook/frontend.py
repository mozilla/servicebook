import requests
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_nav import Nav
from flask import Blueprint

#from flaskext.wtf import Form
#from wtforms.ext.appengine.db import model_form

from db import init, Session
import mappings
from nav import nav


frontend = Blueprint('frontend', __name__)

nav.register_element('frontend_top', Navbar(View('Mozilla QA ~ Service Book', '.home'),))


@frontend.route("/")
def home():
    projects = Session.query(mappings.Project)
    return render_template('home.html', projects=projects)


_BUGZILLA = 'https://bugzilla.mozilla.org/rest/bug?product=%s&component=%s'


@frontend.route("/project/<int:project_id>")
def project(project_id):
    q = Session.query(mappings.Project).filter(mappings.Project.id==project_id)
    project = q.one()
    if project.bz_product:
        bugzilla = _BUGZILLA % (project.bz_product, project.bz_component)
        res = requests.get(bugzilla)
        bugs = res.json()['bugs']
    else:
        bugs = []

    return render_template('project.html', project=project, bugs=bugs)





