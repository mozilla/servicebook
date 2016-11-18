import yaml
import requests

from flask import Blueprint
from flask import jsonify

from servicebook.db import Session
from servicebook.mappings import Project, Person, Group


api = Blueprint('api', __name__)


@api.route("/projects.json")
def api_home():
    projects = Session.query(Project).order_by(Project.name.asc())
    jprojects = [project.to_json() for project in projects]
    return jsonify(jprojects)


@api.route("/person/<int:person_id>.json")
def api_person(person_id):
    person = Session.query(Person).filter(Person.id == person_id).one()

    # should be an attribute in the person table
    p = Session.query(Project)
    projects = p.filter((Project.primary_id == person_id) |
                        (Project.secondary_id == person_id))
    projects = projects.order_by(Project.name.asc())

    person = person.to_json()
    person['projects'] = [project.to_json() for project in projects]
    return jsonify(person)


@api.route("/group/<name>.json")
def api_group(name):
    group = Session.query(Group).filter(Group.name == name).one()
    # should be an attribute in the group table
    p = Session.query(Project)
    projects = p.filter(Project.group == group)
    projects = projects.order_by(Project.name.asc())

    group = group.to_json()
    group['projects'] = [project.to_json() for project in projects]
    return jsonify(group)


_BUGZILLA = 'https://bugzilla.mozilla.org/rest/bug?product=%s&component=%s'


@api.route("/project/<int:project_id>.json")
def api_project(project_id):
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

    project = project.to_json()
    project['info'] = project_info
    project['bugs'] = bugs
    return jsonify(**project)
