from flask import Blueprint

org = Blueprint('org', __name__)

from app.org import routes