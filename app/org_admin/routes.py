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
                                       'password': request.form['password'], 'org_username': org_username,
                                       'admins': ''})
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
    server = jenkins.Jenkins(data['build_server_name'], username=profile_cred['username'],
                             password=profile_cred['password'])
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


@org_admin.route('/<org_username>/edit_cred/<org_admin_username>/<profile_name>', methods=['GET', 'POST'])
@login_required
def edit_cred(org_username, org_admin_username, profile_name):
    org_info = mongo.db.orgs.find_one({'username': org_username})
    admin = mongo.db.users.find_one({'username': org_admin_username})
    cred_info = mongo.db.creds.find_one({'$and': [{'profile_name': profile_name}, {'org_username': org_username}]})
    if request.method == 'POST':
        new_password = request.form['newPassword']
        renew_password = request.form['renewPassword']
        if new_password == renew_password:
            mongo.db.creds.update_one({'$and': [{'profile_name': profile_name}, {'org_username': org_username}]},
                                      {'$set': {'password': new_password}}, upsert=False)
            return redirect(
                url_for('org_admin.credentials', org_username=org_username, org_admin_username=org_admin_username))
        else:
            print('New Password never matched')
    return render_template('org_admin/edit_credentials.html', org_info=org_info, admin=admin, cred_info=cred_info)


@org_admin.route('/delete_cred', methods=['GET'])
@login_required
def delete_cred():
    data = request.args
    data = data.to_dict()
    admins_list = mongo.db.creds.find_one(
        {'$and': [{'profile_name': data['profile_name']}, {'org_username': data['org_username']}]},
        {'admins': 1, '_id': 0})
    active_admins = admins_list['admins']
    if active_admins:
        return jsonify({'status': 401})
    else:
        mongo.db.creds.delete_one({'$and': [{'profile_name': data['profile_name']}, {'org_username': data['org_username']}]})
        return jsonify({'status': 200})


@org_admin.route('/verify_source', methods=['GET'])
@login_required
def verify_source():
    data = request.args
    data = data.to_dict()
    profile_cred = mongo.db.creds.find_one(
        {'$and': [{'profile_name': data['cred']}, {'org_username': data['org_username']}]})
    apps = requests.get('http://{server_name}/activiti-app/api/enterprise/models?filter=myApps&modelType=3'.format(
        server_name=data['server_name']),
                        auth=(profile_cred['username'], profile_cred['password']))
    if apps.status_code == 200:
        apps_names = []
        for app in  apps.json()['data']:
            apps_names.append(app['name'])
        print(apps_names)
        return jsonify({'status': 200, 'apps_names': apps_names})
    else:
        return jsonify({'status': apps.status_code})
