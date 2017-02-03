from flask import Blueprint, request, jsonify
from servicebook.mappings import Project


search = Blueprint('search', __name__)


@search.route('/api/search')
def _search():
    query = request.args.get('q')
    if query is None:
        res = []
    else:
        res = [p.to_json() for p in Project.search_query(query)]

    return jsonify({'data': res, 'meta': {'total': len(res)}})
