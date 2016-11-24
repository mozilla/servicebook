from .users import users_bp
from .api import api
from .actions import actions
from .projects import projects
from .auth import auth
from .frontend import frontend
from .groups import groups


blueprints = (users_bp, actions, api, projects, auth, frontend, groups)
