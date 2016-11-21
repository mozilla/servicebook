import json

import yaml
import requests

from sqlalchemy.sql import collate
from flask import render_template
from flask_nav.elements import View, Navbar
from flask import Blueprint
from flask import request, redirect

from servicebook.db import Session
from servicebook.mappings import Project, Person, Group
from servicebook.nav import nav
from servicebook.forms import ProjectForm


frontend = Blueprint('frontend', __name__)
nav.register_element('frontend_top',
                     Navbar(View('Mozilla QA ~ Service Book', '.home'),))


@frontend.route("/")
def home():
    field = collate(Project.name, 'NOCASE')
    projects = Session.query(Project).order_by(field.asc())
    return render_template('home.html', projects=projects)


@frontend.route("/person/<int:person_id>")
def person(person_id):
    person = Session.query(Person).filter(Person.id == person_id).one()

    # should be an attribute in the person table
    p = Session.query(Project)
    projects = p.filter((Project.primary_id == person_id) |
                        (Project.secondary_id == person_id))
    projects = projects.order_by(Project.name.asc())

    return render_template('person.html', projects=projects, person=person)


@frontend.route("/group/<name>")
def group(name):
    group = Session.query(Group).filter(Group.name == name).one()
    # should be an attribute in the group table
    p = Session.query(Project)
    projects = p.filter(Project.group_name == name)
    projects = projects.order_by(Project.name.asc())
    return render_template('group.html', projects=projects, group=group)


_STATUSES = 'status=NEW&status=REOPENED&status=UNCONFIRMED&status=ASSIGNED'
_BUGZILLA = ('https://bugzilla.mozilla.org/rest/bug?' + _STATUSES +
             '&product=%s&component=%s&limit=10')



@frontend.route("/project/<int:project_id>/edit", methods=['GET', 'POST'])
def edit_project(project_id):
    q = Session.query(Project).filter(Project.id == project_id)
    project = q.one()

    form = ProjectForm(request.form, project)
    if request.method == 'POST' and form.validate():
        form.populate_obj(project)
        Session.add(project)
        Session.commit()
        return redirect('/project/%d' % project.id)

    action = 'Edit %r' % project.name
    return render_template("project_edit.html", form=form, action=action,
                           form_action='/project/%d/edit' % project.id)


@frontend.route("/project/", methods=['GET', 'POST'])
def add_project():
    form = ProjectForm(request.form)
    if request.method == 'POST' and form.validate():
        project = Project()
        form.populate_obj(project)
        Session.add(project)
        Session.commit()
        return redirect('/project/%d' % project.id)

    action = 'Add a new project'
    return render_template("project_edit.html", form=form, action=action,
                           form_action="/project/")


@frontend.route("/project/<int:project_id>")
def project(project_id):
    q = Session.query(Project).filter(Project.id == project_id)
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
