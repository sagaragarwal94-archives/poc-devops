from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, current_user
from app.org_admin import org_admin
from app import mongo, bcrypt, login_manager
import requests
import jenkins


@org_admin.route('/<org_username>/credentials/<org_admin_username>', methods=['GET', 'POST'])
@login_required
def credentials(org_username, org_admin_username):
    org_info = mongo.db.orgs.find_one({'username': org_username})
    admin = mongo.db.users.find_one({'username': org_admin_username})
    credentials_info = mongo.db.creds.find({'org_username': org_username}, {'profile_name': 1, 'username': 1, '_id': 0})
    if request.method == 'POST':
        username = request.form['username']
        profile_name = request.form['profile_name']
        if request.form['password'] == request.form['re_password']:
            profile_exist = mongo.db.creds.find_one(
                {'$and': [{'profile_name': profile_name}, {'org_username': org_username}]})
            if not profile_exist:
                mongo.db.creds.insert({'profile_name': profile_name, 'username': username,
                                       'password': request.form['password'], 'org_username': org_username})
            else:
                print("Profile Exists")
        else:
            print("Password different")
    return render_template('org_admin/credentials.html', org_info=org_info, admin=admin,
                           credentials_info=credentials_info)


@org_admin.route('/<org_username>/profile/<org_admin_username>', methods=['GET', 'POST'])
@login_required
def profile(org_username, org_admin_username):
    org_info = mongo.db.orgs.find_one({'username': org_username})
    admin = mongo.db.users.find_one({'username': org_admin_username})
    credentials_info = mongo.db.creds.find({'org_username': org_username})
    creds_list = []
    for cred in credentials_info:
        creds_list.append(cred)
    # apps = requests.get('http://172.16.0.39:8080/activiti-app/api/enterprise/models?filter=myApps&modelType=3',
    #                     auth=('admin', 'password'))
    apps = {}
    return render_template('org_admin/profiles.html', org_info=org_info, admin=admin, credentials_info=creds_list,
                           apps=apps)


@org_admin.route('/verify_build', methods=['GET'])
@login_required
def verify_build():
    data = request.args
    data = data.to_dict()
    profile_cred = mongo.db.creds.find_one(
        {'$and': [{'profile_name': data['cred']}, {'org_username': data['org_username']}]})
    server = jenkins.Jenkins(data['build_server_name'], username=profile_cred['username'], password=profile_cred['password'])
    try:
        server.get_whoami()
        return jsonify({'status': 200})
    except jenkins.JenkinsException:
        return jsonify({'status': 401})


@org_admin.route('/verify_scm', methods=['GET'])
@login_required
def verify_scm():
    data = request.args
    data = data.to_dict()
    profile_cred = mongo.db.creds.find_one(
        {'$and': [{'profile_name': data['cred']}, {'org_username': data['org_username']}]})
    r = requests.get('https://api.github.com/repos/{scm_username}/{scm_repo_name}/branches/{scm_branch_name}'.format(
        scm_username=profile_cred['username'], scm_repo_name=data['scm_repo_name'], scm_branch_name=data['branch_name']
    ),
        auth=(profile_cred['username'], profile_cred['password']))

    return jsonify({'status': r.status_code})
