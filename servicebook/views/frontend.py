from sqlalchemy.sql import collate
from flask import render_template
from flask import Blueprint

from servicebook.db import Session
from servicebook.mappings import Project


frontend = Blueprint('frontend', __name__)


@frontend.route("/")
def home():
    field = collate(Project.name, 'NOCASE')
    projects = Session.query(Project).order_by(field.asc())
    return render_template('home.html', projects=projects)
