import json
import yaml
import requests
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_nav.elements import Navbar, View, Subgroup, Link, Text, Separator
from flask_nav import Nav
from flask import Blueprint
from flask import request

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


@frontend.route("/swagger")
def swagger():
    endpoint = request.args.get('endpoint')
    res = requests.get(endpoint)
    spec = yaml.load(res.content)
    return render_template('swagger.html', swagger_url=endpoint,
            spec=json.dumps(spec))



@frontend.route("/project/<int:project_id>")
def project(project_id):
    q = Session.query(mappings.Project).filter(mappings.Project.id==project_id)
    project = q.one()

    # scraping bugzilla info
    if project.bz_product:
        bugzilla = _BUGZILLA % (project.bz_product, project.bz_component)
        res = requests.get(bugzilla)
        bugs = res.json()['bugs']
    else:
        bugs = []

    # if we have some deployments, scraping project info out of the
    # stage one (fallback to the first one)
    swagger = None

    if len(project.deployments) > 0:
        for depl in project.deployments:
            if depl.name == 'stage':
                swagger = depl.endpoint.lstrip('/') + '/__api__'
                break

        if swagger is None:
            swagger = project.deployments[0].endpoint.lstrip('/') + '/__api__'

    project_info = None

    if swagger is not None:
        res = requests.get(swagger)
        if res.status_code == 200:
            project_info = yaml.load(res.content)['info']

    return render_template('project.html', project=project, bugs=bugs,
                           project_info=project_info)
