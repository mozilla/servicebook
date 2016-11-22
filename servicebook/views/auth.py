from flask import Blueprint
from flask import request, redirect, session, url_for, flash

from servicebook.auth import github, github2dbuser
from servicebook.mappings import Person
from servicebook.db import Session

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    redirect_uri = url_for('auth.authorized', next=request.args.get('next') or
        request.referrer or None, _external=True)
    # More scopes http://developer.github.com/v3/oauth/#scopes
    params = {'redirect_uri': redirect_uri, 'scope': 'user:email'}
    print(github.get_authorize_url(**params))
    return redirect(github.get_authorize_url(**params))


@auth.route('/logout')
def logout():
    del session['token']
    del session['user_id']
    flash('Logged out')
    return redirect('/')


@auth.route('/github/callback')
def authorized():
    # check to make sure the user authorized the request
    if not 'code' in request.args:
        flash('You did not authorize the request')
        return redirect('/')

    # make a request for the access token credentials using code
    redirect_uri = url_for('auth.authorized', _external=True)

    data = dict(code=request.args['code'],
        redirect_uri=redirect_uri,
        scope='user:email,public_repo')

    auth = github.get_auth_session(data=data)
    github_user = auth.get('user').json()
    db_user = github2dbuser(github_user)

    session['token'] = auth.access_token
    session['user_id'] = db_user.id
    flash('Logged in as ' + str(db_user))
    return redirect('/')
