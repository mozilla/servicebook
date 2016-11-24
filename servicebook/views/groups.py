from flask import render_template
from flask import Blueprint

from servicebook.db import Session
from servicebook.mappings import Group, Project


groups = Blueprint('groups', __name__)


@groups.route("/groups/<name>")
def group_view(name):
    group = Session.query(Group).filter(Group.name == name).one()
    # should be an attribute in the group table
    p = Session.query(Project)
    projects = p.filter(Project.group_name == name)
    projects = projects.order_by(Project.name.asc())
    backlink = '/'
    return render_template('group.html', projects=projects, group=group,
                           backlink=backlink)
