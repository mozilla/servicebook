import os
import yaml
import json
import requests

from flask import Blueprint
from flask import request, jsonify
from flask import render_template

from smwogger.main import get_runner


actions = Blueprint('actions', __name__)
test_dir = os.path.join(os.path.dirname(__file__), '..', 'tests')


@actions.route("/action/heartbeat")
def action_hb():
    endpoint = request.args.get('endpoint')
    result = requests.get(endpoint)
    try:
        result = result.json()
        return jsonify(result)
    except ValueError:
        return result.content


@actions.route("/action/smoke")
def action_smoke():
    endpoint = request.args.get('endpoint')

    # XXX plugged two hardcoded files for the demo
    #
    if 'search' in endpoint:
        endpoint = os.path.join(test_dir, 'absearch.yaml')
    elif 'shavar' in endpoint:
        endpoint = os.path.join(test_dir, 'shavar.yaml')

    runner = get_runner(endpoint)
    steps = []
    for index, (oid, options) in enumerate(runner.scenario()):
        step = {'operationId': oid}
        try:
            runner(oid, **options)
            step['result'] = 'OK'
        except Exception as e:
            step['result'] = 'KO'
            step['exception'] = str(e)
        steps.append(step)

    return jsonify({'steps': steps})


@actions.route("/action/swagger")
def swagger():
    endpoint = request.args.get('endpoint')
    res = requests.get(endpoint)
    spec = yaml.load(res.content)
    return render_template('swagger.html', swagger_url=endpoint,
                           spec=json.dumps(spec))
