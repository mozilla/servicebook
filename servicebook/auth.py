from functools import wraps

from rauth.service import OAuth2Service
from flask import session, abort, g

from servicebook.db import Session
from servicebook.mappings import User


def GithubAuth(app):
    github = OAuth2Service(**app.config['oauth'])
    if not hasattr(app, 'extensions'):
        app.extensions = {}
    app.extensions['github'] = github


def github2dbuser(github_user):
    dbsession = Session()
    q = dbsession.query(User)
    q = q.filter(User.github == github_user['login'])
    db_user = q.first()
    if db_user is None:
        # creating an entry
        name = github_user['name'].split(' ', 1)
        if len(name) == 2:
            firstname, lastname = name
        else:
            firstname = lastname = name
        login = github_user['login']
        db_user = User(firstname, lastname, login)
        dbsession.add(db_user)
        dbsession.commit()

    return db_user


def get_user(app):
    if 'token' not in session:
        return None

    github = app.extensions['github']
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
        user = g.user

        if user is None:
            if g.debug:
                print('Anonymous rejected')
            abort(401)
            return

        if not user.editor:
            if g.debug:
                print('%r rejected' % user)
            abort(401)
            return

        return func(*args, **kw)
    return _only_for_editors
