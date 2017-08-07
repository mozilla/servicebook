import os
from flask import Blueprint, jsonify, Response
from servicebook.mappings import Project
from servicebook.db import Session


here = os.path.abspath(os.path.dirname(__file__))
circleci_artifact = 'version.json'
heartbeat = Blueprint('heartbeat', __name__)


@heartbeat.route('/__version__')
def _version():
    if os.path.exists(circleci_artifact):
        filename = circleci_artifact
    else:
        filename = os.path.join(here, '..', 'templates', 'version.json')

    with open(filename) as f:
        return Response(f.read(), mimetype='application/json')


@heartbeat.route('/__lbheartbeat__')
def _lbheartbeat():
    return ''


@heartbeat.route('/__heartbeat__')
def _heartbeat():
    results = {}
    q = Session().query(Project)
    results['database'] = q.count() > 0
    return jsonify(results)
