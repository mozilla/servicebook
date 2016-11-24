from flask import Blueprint
from flask import request, redirect, session, url_for, flash
from flask import render_template

from servicebook.auth import github2dbuser

auth = Blueprint('auth', __name__)


@auth.route('/login')
def login():
    github = auth.app.extensions['github']

    redirect_uri = (url_for('auth.authorized', next=request.args.get('next')
                    or request.referrer or None, _external=True))
    # More scopes http://developer.github.com/v3/oauth/#scopes
    params = {'redirect_uri': redirect_uri, 'scope': 'user:email'}
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
    if 'code' not in request.args:
        flash('You did not authorize the request')
        return redirect('/')

    github = auth.app.extensions['github']

    # make a request for the access token credentials using code
    redirect_uri = url_for('auth.authorized', _external=True)

    data = dict(code=request.args['code'],
                redirect_uri=redirect_uri,
                scope='user:email,public_repo')

    authorization = github.get_auth_session(data=data)
    github_user = authorization.get('user').json()
    db_user = github2dbuser(github_user)

    session['token'] = authorization.access_token
    session['user_id'] = db_user.id
    flash('Logged in as ' + str(db_user))
    return redirect('/')


def unauthorized_view(error):
    return render_template('unauthorized.html', backlink='/'), 401
