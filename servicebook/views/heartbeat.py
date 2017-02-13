import subprocess
import json
from flask import Blueprint, render_template, jsonify
from servicebook import __version__


heartbeat = Blueprint('heartbeat', __name__)


@heartbeat.route('/__version__')
def _version():
    commit = subprocess.check_output(["git", "describe", "--always"])
    resp = render_template('version.json', version=__version__,
                           commit=str(commit.strip(), 'utf8'))
    data = json.loads(resp)
    return jsonify(data)
