import yaml
import requests

from sqlalchemy.sql import collate
from flask import render_template
from flask import Blueprint
from flask import request, redirect

from servicebook.db import Session
from servicebook.mappings import Project, User, Group, Deployment
from servicebook.forms import ProjectForm, DeploymentForm, UserForm
from servicebook.auth import only_for_editors


frontend = Blueprint('frontend', __name__)

_MOZILLIANS_API_KEY = 'PUTYOURKEYHERE'
_MOZILLIANS_API = 'https://mozillians.org/api/v2/users'
_MOZILLIANS_CACHE = {}


def get_mozillians_info(email):
    if email in _MOZILLIANS_CACHE:
        url = _MOZILLIANS_CACHE[email]
    else:
        url = '?api-key=%s&email=%s&format=json'
        url = url % (_MOZILLIANS_API_KEY, email)
        user = requests.get(_MOZILLIANS_API + url).json()
        if 'results' not in user:
            return {}

        res = user['results']
        if len(res) == 0:
            return {}

        url = res[0]['_url']
        _MOZILLIANS_CACHE[email] = url

    url = url + '?api-key=%s&format=json'
    url = url % _MOZILLIANS_API_KEY
    details = requests.get(url).json()
    return details


@frontend.route("/users")
@only_for_editors
def users():
    field = collate(User.firstname, 'NOCASE')
    users = Session.query(User).order_by(field.asc())
    return render_template('users.html', users=users)


@frontend.route("/users/<int:user_id>/edit", methods=['GET', 'POST'])
@only_for_editors
def edit_user(user_id):
    q = Session.query(User).filter(User.id == user_id)
    user = q.one()

    form = UserForm(request.form, user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        Session.add(user)
        Session.commit()
        return redirect('/users')

    action = 'Edit %r' % user
    return render_template("project_edit.html", form=form, action=action,
                           form_action='/users/%d/edit' % user.id,
                           backlink='/users/%d' % user.id)


@frontend.route("/users/<int:user_id>")
def user(user_id):
    user = Session.query(User).filter(User.id == user_id).one()

    if user.email:
        mozillians = get_mozillians_info(user.email)
    else:
        mozillians = {}

    # should be an attribute in the user table
    p = Session.query(Project)
    projects = p.filter((Project.primary_id == user_id) |
                        (Project.secondary_id == user_id))
    projects = projects.order_by(Project.name.asc())
    backlink = '/'
    return render_template('user.html', projects=projects, user=user,
                           backlink=backlink, mozillians=mozillians)


@frontend.route("/")
def home():
    field = collate(Project.name, 'NOCASE')
    projects = Session.query(Project).order_by(field.asc())
    return render_template('home.html', projects=projects)


@frontend.route("/group/<name>")
def group(name):
    group = Session.query(Group).filter(Group.name == name).one()
    # should be an attribute in the group table
    p = Session.query(Project)
    projects = p.filter(Project.group_name == name)
    projects = projects.order_by(Project.name.asc())
    backlink = '/'
    return render_template('group.html', projects=projects, group=group,
                           backlink=backlink)


_STATUSES = 'status=NEW&status=REOPENED&status=UNCONFIRMED&status=ASSIGNED'
_BUGZILLA = ('https://bugzilla.mozilla.org/rest/bug?' + _STATUSES +
             '&product=%s&component=%s&limit=10')


@frontend.route("/project/<int:project_id>/edit", methods=['GET', 'POST'])
@only_for_editors
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
    backlink = '/project/%d' % project.id
    return render_template("project_edit.html", form=form, action=action,
                           backlink=backlink,
                           form_action='/project/%d/edit' % project.id)


@frontend.route("/project/", methods=['GET', 'POST'])
@only_for_editors
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

    backlink = '/'
    edit = '/project/%d/edit' % project.id
    return render_template('project.html', project=project, bugs=bugs,
                           edit=edit,
                           project_info=project_info, backlink=backlink)


@frontend.route("/project/<int:project_id>/deployment",
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
        return redirect('/project/%d' % project.id)

    action = 'Add a new deployment for %s' % str(project)
    return render_template("deployment_edit.html", form=form, action=action,
                           form_action="/project/%s/deployment" % project_id)


@frontend.route("/project/<int:project_id>/deployment/<int:depl_id>/delete",
                methods=['GET'])
@only_for_editors
def remove_deployment(project_id, depl_id):
    q = Session.query(Deployment).filter(Deployment.id == depl_id)
    depl = q.one()
    Session.delete(depl)
    Session.commit()
    return redirect('/project/%d' % (project_id))


@frontend.route("/project/<int:project_id>/deployment/<int:depl_id>/edit",
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
        return redirect('/project/%d' % (project.id))

    form_action = '/project/%d/deployment/%d/edit'
    backlink = '/project/%d' % project.id
    action = 'Edit %r for %s' % (depl.name, project.name)
    return render_template("deployment_edit.html", form=form, action=action,
                           project=project, backlink=backlink,
                           form_action=form_action % (project.id, depl.id))
