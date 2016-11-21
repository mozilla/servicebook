import yaml
import json
import requests

from flask import Blueprint
from flask import request, jsonify
from flask import render_template

from smwogger.main import get_runner


actions = Blueprint('actions', __name__)


@actions.route("/action/heartbeat")
def action_hb():
    endpoint = request.args.get('endpoint')
    result = requests.get(endpoint).json()
    return jsonify(result)


@actions.route("/action/smoke")
def action_smoke():
    #endpoint = request.args.get('endpoint')
    endpoint = '/Users/tarek/Dev/github.com/smwogger/smwogger/tests/absearch.yaml'
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


