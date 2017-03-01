import subprocess
import json
from flask import Blueprint, render_template, jsonify

from servicebook import __version__
from servicebook.mappings import Project
from servicebook.db import Session


commit = subprocess.check_output(["git", "describe", "--always"])
commit = str(commit.strip(), 'utf8')
heartbeat = Blueprint('heartbeat', __name__)


@heartbeat.route('/__version__')
def _version():
    resp = render_template('version.json', version=__version__,
                           commit=commit)
    data = json.loads(resp)
    return jsonify(data)


@heartbeat.route('/__lbheartbeat__')
def _lbheartbeat():
    return ''


@heartbeat.route('/__heartbeat__')
def _heartbeat():
    results = {}
    q = Session().query(Project)
    results['database'] = q.count() > 0
    return jsonify(results)
