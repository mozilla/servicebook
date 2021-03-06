import json
import os
import logging.config
import sys
import argparse
import time
from functools import partial, wraps

from werkzeug.exceptions import HTTPException
from flask import Flask, g, request, Response, abort, jsonify
from flask_iniconfig import INIConfig
from flask_restless_swagger import SwagAPIManager as APIManager
from raven.contrib.flask import Sentry

from servicebook.db import init, Session, _SEARCH
from servicebook.mappings import published
from servicebook.views.search import search
from servicebook.views.heartbeat import heartbeat
from servicebook.search import get_indexer
from servicebook.auth import authenticate

from flask_restless.views import base
from flask_restless import DefaultSerializer
from flask_restless.helpers import get_by
from sqlalchemy.inspection import inspect as sa_inspect


sentry = Sentry()


# see https://github.com/jfinkels/flask-restless/issues/619
# hack until flask-restless provides the API class in
# pre/post processors

def _tries(exception, session, func, *args, **kw):
    attempts = 0
    session.rollback()

    while attempts < 6:
        time.sleep(attempts * 2.)
        try:
            res = func(*args, **kw)
            session.commit()
            return res
        except Exception:
            session.rollback()
            attempts += 1

    raise exception


def _catch_integrity_errors(session):
    def decorated(func):
        @wraps(func)
        def wrapped(*args, **kw):
            try:
                try:
                    g.api = func.im_self
                except Exception:
                    g.api = func.__self__

                res = func(*args, **kw)
                session.commit()
                return res
            except base.SQLAlchemyError as exception:
                try:
                    return _tries(exception, session, func, *args, **kw)
                except Exception:
                    pass

                if sentry.client:
                    sentry.captureException()
                status = 409 if base.is_conflict(exception) else 400
                detail = str(exception)
                title = base.un_camel_case(exception.__class__.__name__)
                return base.error_response(status, cause=exception,
                                           detail=detail,
                                           title=title)
        return wrapped
    return decorated


base.catch_integrity_errors = _catch_integrity_errors


HERE = os.path.dirname(__file__)
DEFAULT_INI_FILE = os.path.join(HERE, '..', 'servicebook.ini')
_DEBUG = True


def add_timestamp(strict, method, *args, **kw):
    # getting the existing last_modified if the resource exists
    model = g.api.model
    session = g.api.session

    if 'resource_id' in kw:
        query = session.query(model)
        entry = query.filter(model.id == kw['resource_id']).one()

        # if this is an update, we want a If-Match header
        if entry is not None and strict == 1:
            etag = str(entry.last_modified)

            if not request.if_match:
                abort(428)

            if etag not in request.if_match:
                abort(412)

    g.last_modified = int(time.time() * 1000)
    if not method.startswith('DELETE_') and isinstance(kw['data'], dict):
        kw['data']['last_modified'] = g.last_modified


class NotModified(HTTPException):
    code = 304

    def get_response(self, environment):
        return Response(status=304)


class JsonSerializer(DefaultSerializer):
    def serialize(self, instance, only=None):
        return {'data': instance.to_json()}


def create_app(ini_file=DEFAULT_INI_FILE):
    app = Flask(__name__)
    INIConfig(app)
    app.config.from_inifile(ini_file)
    app.secret_key = app.config['common']['secret_key']
    if app.config.get('sentry', {}).get('dsn') is not None:
        sentry.init_app(app, dsn=app.config['sentry']['dsn'],
                        logging=True, level=logging.ERROR)
    strict = int(app.config['common'].get('strict_update', 0))
    sqluri = os.environ.get('SQLURI')
    if sqluri is None:
        sqluri = app.config['common']['sqluri']
    app.db = init(sqluri)

    preprocessors = {}
    for method in ('POST_RESOURCE', 'PATCH_RESOURCE', 'DELETE_RESOURCE',
                   'POST_RELATIONSHIP', 'PATCH_RELATIONSHIP',
                   'DELETE_RELATIONSHIP'):
        preprocessors[method] = [partial(add_timestamp, strict, method)]

    app.db.session = Session()
    if 'whoosh' in app.config and 'path' in app.config['whoosh']:
        _SEARCH['WHOOSH_BASE'] = app.config['whoosh']['path']

    get_indexer(_SEARCH, app.db.session)
    app.register_blueprint(search)
    app.register_blueprint(heartbeat)

    manager = APIManager(app, flask_sqlalchemy_db=app.db,
                         preprocessors=preprocessors)

    methods = ['GET', 'POST', 'DELETE', 'PATCH', 'PUT']

    for model in published:
        manager.create_api(model, methods=methods,
                           serializer_class=JsonSerializer,
                           page_size=50,
                           allow_to_many_replacement=True,
                           allow_delete_from_to_many_relationships=True)

    @app.route('/api/')
    def get_models():
        models = []
        for model in published:
            name = model.__table__.name
            inspected = sa_inspect(model)
            # XXX collection name may vary
            primary_key = [key.name for key in inspected.primary_key]
            model = {'name': name, 'primary_key': primary_key,
                     'collection_name': name}
            model['relationships'] = {}

            for name, relationship in inspected.relationships.items():
                rel = {'target': relationship.target.name}
                model['relationships'][name] = rel

            models.append(model)

        return jsonify({'models': models})

    @app.after_request
    def set_etag(response):
        if request.blueprint in ('swagger', 'heartbeat'):
            return response

        if request.path.rstrip('/') == '/api':
            return response

        if response.status_code > 399:
            return response

        # suboptimal: redeserialization
        # XXX use six
        try:
            result = json.loads(str(response.data, 'utf8'))
        except TypeError:
            result = json.loads(str(response.data))

        data = result.get('data')
        last_modified = None

        # hackish - it depends on url routes XXX
        relation_name = request.view_args.get('relation_name')
        resource_id = request.view_args.get('resource_id')
        api = 'api' in g and g.api or None

        # the relationship was changed
        if (request.method in ('POST', 'PATCH') and relation_name and
                response.status_code == 204):
            # let's update the parent timestamp
            instance = get_by(api.session, api.model, resource_id)
            instance.last_modified = g.last_modified

        # we're sending back some data
        if data is not None:
            if 'last_modidied' in data:
                last_modified = data['last_modified']
            elif api:
                instance = get_by(api.session, api.model, resource_id)
                if instance and hasattr(instance, 'last_modified'):
                    last_modified = instance.last_modified

        # empty response
        else:
            if response.status_code == 204:
                # we did change it, we need to resend the ETag
                last_modified = g.last_modified
            else:
                last_modified = None

            if 'Content-Type' in response.headers:
                response.headers.remove('Content-Type')

        etag = last_modified and str(last_modified) or None

        # checking If-None-Match on GET calls
        if (request.method == 'GET' and request.if_none_match):
            if etag and etag in request.if_none_match:
                return NotModified()

        # adding an ETag header
        if etag:
            response.set_etag(etag)

        return response

    @app.before_request
    def before_req():
        authenticate(app, request)
        g.debug = _DEBUG

    logging.config.fileConfig(ini_file)
    return app


def main(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='ServiceBook Server.')

    parser.add_argument('--config-file', help='Config file',
                        type=str, default=DEFAULT_INI_FILE)
    parser.add_argument(
        '--no-run', action='store_true', default=False)

    args = parser.parse_args(args=args)
    app = create_app(ini_file=args.config_file)
    host = app.config['common'].get('host', '0.0.0.0')
    port = app.config['common'].get('port', 5001)
    debug = app.config.get('DEBUG', _DEBUG)

    if args.no_run:
        return app

    app.run(debug=debug, host=host, port=port)


if __name__ == "__main__":
    main()
