import yaml
import requests

from flask import render_template
from flask import Blueprint
from flask import request, redirect

from servicebook.db import Session
from servicebook.mappings import Project, Deployment
from servicebook.forms import ProjectForm, DeploymentForm
from servicebook.auth import only_for_editors


projects = Blueprint('projects', __name__)


_STATUSES = 'status=NEW&status=REOPENED&status=UNCONFIRMED&status=ASSIGNED'
_BUGZILLA = ('https://bugzilla.mozilla.org/rest/bug?' + _STATUSES +
             '&product=%s&component=%s&limit=10')


@projects.route("/projects/<int:project_id>/edit", methods=['GET', 'POST'])
@only_for_editors
def edit_project(project_id):
    q = Session.query(Project).filter(Project.id == project_id)
    project = q.one()

    form = ProjectForm(request.form, project)
    if request.method == 'POST' and form.validate():
        form.populate_obj(project)
        Session.add(project)
        Session.commit()
        return redirect('/projects/%d' % project.id)

    action = 'Edit %r' % project.name
    backlink = '/projects/%d' % project.id
    return render_template("edit.html", form=form, action=action,
                           backlink=backlink,
                           form_action='/projects/%d/edit' % project.id)


@projects.route("/projects/", methods=['GET', 'POST'])
@only_for_editors
def add_project():
    form = ProjectForm(request.form)
    if request.method == 'POST' and form.validate():
        project = Project()
        form.populate_obj(project)
        Session.add(project)
        Session.commit()
        return redirect('/projects/%d' % project.id)

    action = 'Add a new project'
    return render_template("edit.html", form=form, action=action,
                           form_action="/projects/")


@projects.route("/projects/<int:project_id>")
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

    backlink = '/'
    edit = '/projects/%d/edit' % project.id
    return render_template('project.html', project=project, bugs=bugs,
                           edit=edit,
                           project_info=project_info, backlink=backlink)


@projects.route("/projects/<int:project_id>/deployments",
                methods=['GET', 'POST'])
@only_for_editors
def add_deployment(project_id):
    q = Session.query(Project).filter(Project.id == project_id)
    project = q.one()

    form = DeploymentForm(request.form)
    if request.method == 'POST' and form.validate():
        deployment = Deployment()
        deployment.project = project
        form.populate_obj(deployment)
        Session.add(project)
        Session.commit()
        return redirect('/projects/%d' % project.id)

    action = 'Add a new deployment for %s' % str(project)
    return render_template("edit.html", form=form, action=action,
                           form_action="/projects/%s/deployment" % project_id)


@projects.route("/projects/<int:project_id>/deployments/<int:depl_id>/delete",
                methods=['GET'])
@only_for_editors
def remove_deployment(project_id, depl_id):
    q = Session.query(Deployment).filter(Deployment.id == depl_id)
    depl = q.one()
    Session.delete(depl)
    Session.commit()
    return redirect('/projects/%d' % (project_id))


@projects.route("/projects/<int:project_id>/deployments/<int:depl_id>/edit",
                methods=['GET', 'POST'])
@only_for_editors
def edit_deployment(project_id, depl_id):
    q = Session.query(Deployment).filter(Deployment.id == depl_id)
    depl = q.one()
    project = depl.project

    form = DeploymentForm(request.form, depl)
    if request.method == 'POST' and form.validate():
        form.populate_obj(depl)
        Session.add(depl)
        Session.commit()
        return redirect('/projects/%d' % (project.id))

    form_action = '/projects/%d/deployments/%d/edit'
    backlink = '/projects/%d' % project.id
    action = 'Edit %r for %s' % (depl.name, project.name)
    return render_template("edit.html", form=form, action=action,
                           project=project, backlink=backlink,
                           form_action=form_action % (project.id, depl.id))
