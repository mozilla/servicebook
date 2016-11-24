from sqlalchemy.sql import collate
from flask import render_template
from flask import Blueprint
from flask import request, redirect

from servicebook.db import Session
from servicebook.mappings import User, Project
from servicebook.forms import UserForm
from servicebook.auth import only_for_editors


users_bp = Blueprint('users', __name__)


@users_bp.route("/users/<int:user_id>")
def user_view(user_id):
    user = Session.query(User).filter(User.id == user_id).one()
    mozillians = users_bp.app.extensions['mozillians']

    if user.email:
        mozillian = mozillians.get_info(user.email)
    else:
        mozillian = {}

    # should be an attribute in the user table
    p = Session.query(Project)
    projects = p.filter((Project.primary_id == user_id) |
                        (Project.secondary_id == user_id))
    projects = projects.order_by(Project.name.asc())
    backlink = '/'
    return render_template('user.html', projects=projects, user=user,
                           backlink=backlink, mozillian=mozillian)


@users_bp.route("/users")
@only_for_editors
def users_view():
    field = collate(User.firstname, 'NOCASE')
    users = Session.query(User).order_by(field.asc())
    return render_template('users.html', users=users)


@users_bp.route("/users/<int:user_id>/edit", methods=['GET', 'POST'])
@only_for_editors
def edit_user(user_id):
    q = Session.query(User).filter(User.id == user_id)
    user = q.one()

    form = UserForm(request.form, user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        Session.add(user)
        Session.commit()
        return redirect('/users')

    action = 'Edit %r' % user
    return render_template("edit.html", form=form, action=action,
                           form_action='/users/%d/edit' % user.id,
                           backlink='/users/%d' % user.id)
