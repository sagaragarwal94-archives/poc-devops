from app import bcrypt
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, username):
        self.username = username

    @staticmethod
    def is_authenticated(self):
        self.authenticated = True

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return bcrypt.check_password_hash(password_hash, password)