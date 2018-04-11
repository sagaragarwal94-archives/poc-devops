from flask import render_template, request, redirect, url_for
from flask_login import login_user, login_required, logout_user
from app.user import user
from app import mongo, bcrypt, login_manager
from app.user.user_loging_manager import User


@login_manager.user_loader
def load_user(username):
    users = mongo.db.users.find_one({'username': username})
    if not users:
        return None
    return User(users['username'])


@user.route('/', methods=['POST', 'GET'])
@user.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['inputUsername']
        password = request.form['inputPassword']
        user = mongo.db.users.find_one({'username': username})
        if user:
            # if User.validate_login(user['password'], password):
            if user['password'] == password:
                user_obj = User(username)
                login_user(user_obj)
                if user['role'] == 'admin' and user['status'] == 'active':
                    return redirect(url_for('admin.profile', username=username))
                else:
                    print('you are not admin or suspended, kindly contact administrator')
        else:
            print('wrong password')
            return redirect(url_for('user.login'))
    return render_template('user/login.html')


@login_required
@user.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('user.login'))