from flask import Flask
from flask_pymongo import PyMongo
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
import os

app = Flask(__name__)

app.config.from_pyfile('config.py')
app.secret_key = os.urandom(24)

mongo = PyMongo(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

from app.user import user as user_blueprint

app.register_blueprint(user_blueprint)

from app.admin import admin as admin_blueprint

app.register_blueprint(admin_blueprint)

login_manager.login_view = "user.login"
