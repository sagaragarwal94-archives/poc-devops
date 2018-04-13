from flask import Blueprint

org_admin = Blueprint('org_admin', __name__)

from app.org_admin import routes
