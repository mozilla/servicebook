from functools import wraps

from rauth.service import OAuth2Service
from flask import session
from werkzeug.exceptions import Unauthorized

from servicebook.db import Session
from servicebook.mappings import Person


github = OAuth2Service(
    name='Servicebook',
    base_url='https://api.github.com/',
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_id='cfcdbb666682b71f6d69',
    client_secret='0544b34f3f8db81e24da4a1f57412cddab6ea0f8'
)


def github2dbuser(github_user):
    dbsession = Session()
    q = dbsession.query(Person)
    q = q.filter(Person.github == github_user['login'])
    db_user = q.first()
    if db_user is None:
        # creating an entry
        name = github_user['name'].split(' ', 1)
        if len(name) == 2:
            firstname, lastname = name
        else:
            firstname = lastname = name
        login = github_user['login']
        db_user = Person(firstname, lastname, login)
        dbsession.add(db_user)
        dbsession.commit()

    return db_user


def get_user():
    if 'token' not in session:
        return None

    auth = github.get_session(token=session['token'])
    resp = auth.get('/user')
    if resp.status_code == 200:
        user = resp.json()
        return github2dbuser(user)
    else:
        return None


def only_for_editors(func):
    @wraps(func)
    def _only_for_editors(*args, **kw):
        user = get_user()
        if user is None or not user.editor:
            raise Unauthorized()

        return func(*args, **kw)
    return _only_for_editors
