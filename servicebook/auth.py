import base64
from flask import abort
from servicebook.mappings import AuthenticationKey


def authenticate(app, request):
    # access configuration
    access = app.config['common'].get('anonymous_access', 'read')

    # write
    if request.method in ('POST', 'PATCH', 'PUT', 'DELETE'):
        if access == 'readwrite':
            return
        desired_scope = 'readwrite', 'admin'
    # read
    else:
        if access in ('read', 'readwrite'):
            return
        desired_scope = 'read', 'readwrite', 'admin'

    key = request.headers.get('Authorization')
    if key is None:
        return abort(401)

    key = key.split(' ')
    if len(key) != 2:
        return abort(401)
    if key[0].lower() != 'apikey':
        return abort(401)

    try:
        key = base64.b64decode(key[1]).decode('ascii')
    except Exception:
        return abort(401)

    # XXX cache this call for one minute
    q = app.db.session.query(AuthenticationKey)
    q = q.filter(AuthenticationKey.key == key)
    auth = q.first()
    if auth is None:
        return abort(401)

    if auth.scope not in desired_scope:
        return abort(401)
