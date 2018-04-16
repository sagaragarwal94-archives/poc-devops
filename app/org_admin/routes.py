from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, current_user
from app.org_admin import org_admin
from app import mongo, bcrypt, login_manager
from app.user.user_loging_manager import User
import requests
import jenkins


@login_required
@org_admin.route('/<org_username>/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    return render_template('org_admin_revamp/dashboard.html', user=user, org_info=org_info)


@login_required
@org_admin.route('/<org_username>/credentials/<username>', methods=['GET', 'POST'])
def credentials(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    creds = mongo.db.creds({'org_username': org_username})
    return render_template('org_admin_revamp/credentials.html', user=user, org_info=org_info, creds=creds)


@login_required
@org_admin.route('/<org_username>/create_creds/<username>', methods=['GET', 'POST'])
def create_creds(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    return render_template('org_admin_revamp/create_creds.html', user=user, org_info=org_info)


@login_required
@org_admin.route('/<org_username>/edit_creds/<username>', methods=['GET', 'POST'])
def edit_creds(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    return render_template('org_admin_revamp/edit_creds.html', user=user, org_info=org_info)


@login_required
@org_admin.route('/authenticate_scm', methods=['GET'])
def authenticate_scm():
    data = request.args
    username = data.to_dict()['username']
    password = data.to_dict()['password']
    r = requests.get('https://api.github.com/user', auth=(username, password))
    if r.status_code == 200:
        return jsonify({'status': 200})
    else:
        return jsonify({'status': 401})


@login_required
@org_admin.route('/authenticate_build', methods=['GET'])
def authenticate_build():
    data = request.args
    username = data.to_dict()['username']
    password = data.to_dict()['password']
    server_name = data.to_dict()['server_name']
    r = jenkins.Jenkins(server_name, username=username, password=password)
    try:
        r.get_whoami()
        return jsonify({'status': 200})
    except jenkins.JenkinsException:
        return jsonify({'status': 401})


@login_required
@org_admin.route('/authenticate_deploy', methods=['GET'])
def authenticate_deploy():
    data = request.args
    username = data.to_dict()['username']
    password = data.to_dict()['password']
    server_name = data.to_dict()['server_name']
    r = requests.get(server_name, auth=(username, password))
    if r.status_code == 200:
        return jsonify({'status': 200})
    else:
        return jsonify({'status': 401})


@login_required
@org_admin.route('/upload_creds', methods=['GET'])
def upload_creds():
    data = request.args
    data = data.to_dict()
    profile_exists = mongo.db.creds.find_one(
        {'$and': [{'profile_name': data['profile_name']}, {'org_username': data['org_username']}]})
    if profile_exists:
        return jsonify({'status': 302})
    else:
        mongo.db.creds.insert(data)
        return jsonify({'status': 200, 'url': '{org_username}/dashboard/{admin}'.format(org_username=data['org_username'], admin=data['admin'])})
