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
    message = ''
    if request.method == 'POST':
        username = request.form['inputUsername']
        password = request.form['inputPassword']
        user = mongo.db.users.find_one({'username': username})
        if user:
            # if User.validate_login(user['password'], password):
            if user['password'] == password:
                user_obj = User(username)
                login_user(user_obj)
                if user['role'] == 'admin':
                    if user['status'] == 'active':
                        return redirect(url_for('admin.profile', username=username))
                    else:
                        message = 'Account Suspended'
                        return render_template('user/login.html', message=message)
                else:
                    message = 'You are not admin.'
                    return render_template('user/login.html', message=message)
            else:
                message = 'Wrong Password, Enter Credentials Again!!'
                return render_template('user/login.html', message=message)
        else:
            message = 'No Account of this Username. Sorry !!'
            return render_template('user/login.html', message=message)
    return render_template('user/login.html', message=message)


@user.route('/login/<org_username>', methods=['POST', 'GET'])
def org_login(org_username):
    message = ''
    org_info = mongo.db.orgs.find_one({'username': org_username})
    if request.method == 'POST':
        username = request.form['inputUsername']
        password = request.form['inputPassword']
        user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
        if user:
            # if User.validate_login(user['password'], password):
            if user['password'] == password:
                user_obj = User(username)
                login_user(user_obj)
                if user['role'] == 'orgadmin':
                    if user['status'] == 'active':
                        return redirect(url_for('org_admin.credentials', org_username=org_username, org_admin_username=username))
                    else:
                        message = 'Account Suspended'
                        return render_template('user/login.html', message=message)
                else:
                    message = 'You are not Organisation Admin.'
                    return render_template('user/login.html', message=message)
            else:
                message = 'Wrong Password, Enter Credentials Again!!'
                return render_template('user/login.html', message=message)
        else:
            message = 'No Account of this Username. Sorry !!'
            return render_template('user/login.html', message=message)
    return render_template('user/login.html', message=message, org_info=org_info)


@user.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('user.login'))
