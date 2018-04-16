from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, current_user
from app.org_admin import org_admin
from app import mongo, bcrypt, login_manager
from app.user.user_loging_manager import User


@login_required
@org_admin.route('/<org_username>/dashboard/<username>', methods=['GET', 'POST'])
def dashboard(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    apps = mongo.db.apps.find({'org_username': org_username})
    return render_template('org_admin/dashboard.html', user=user, org_info=org_info, apps=apps)

@login_required
@org_admin.route('/<org_username>/create_app/<username>', methods=['GET', 'POST'])
def create_app(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    return render_template('org_admin/app_profile.html', user=user, org_info=org_info)

@login_required
@org_admin.route('/<org_username>/scm/<username>', methods=['GET', 'POST'])
def scm(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    scm_profiles = mongo.db.profile.find(
        {'$and': [{'username': username}, {'org_username': org_username}, {'$or': [{'type': 'GIT'}, {'type': 'SVN'}]}]})
    return render_template('org_admin/scm/index.html', user=user, org_info=org_info, scm_profiles=scm_profiles)


@login_required
@org_admin.route('/<org_username>/create_scm/<username>', methods=['GET', 'POST'])
def create_scm(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    if request.method == 'POST':
        scm_username = request.form['username']
        scm_password = request.form['password']
        profilename = request.form['profilename']
        scm_profile = request.form['scm_profile']
        profile_exist = mongo.db.profile.find_one(
            {'$and': [{'profile_name': profilename}, {'$or': [{'type': 'GIT'}, {'type': 'SVN'}]}]})
        if not profile_exist:
            mongo.db.profile.insert({'profile_name': profilename, 'username': username, 'org_username': org_username,
                                     'type': scm_profile, 'scm_username': scm_username, 'scm_password': scm_password})
            return redirect(url_for('org_admin.scm', username=username, org_username=org_username))
        else:
            print("Profile Already Exists")
    return render_template('org_admin/scm/create_scm.html', user=user, org_info=org_info)


@login_required
@org_admin.route('/<org_username>/build/<username>', methods=['GET', 'POST'])
def build(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    build_profiles = mongo.db.profile.find(
        {'$and': [{'username': username}, {'org_username': org_username}, {'type': 'build'}]})
    return render_template('org_admin/build/index.html', user=user, org_info=org_info, build_profiles=build_profiles)


@login_required
@org_admin.route('/<org_username>/create_build/<username>', methods=['GET', 'POST'])
def create_build(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    if request.method == 'POST':
        server_name = request.form['server_name']
        profile_name = request.form['profile_name']
        build_username = request.form['build_username']
        build_password = request.form['build_password']
        build_token =  request.form['build_token']
        profile_exist = mongo.db.profile.find_one(
            {'$and': [{'profile_name': profile_name}, {'type': 'build'}]})
        if not profile_exist:
            mongo.db.profile.insert({'profile_name': profile_name, 'username': username, 'org_username': org_username,
                                     'type': 'build', 'build_username': build_username, 'build_password': build_password,
                                     'server_name': server_name, 'build_token': build_token})
            return redirect(url_for('org_admin.build', username=username, org_username=org_username))
        else:
            print("Profile Already Exists")
    return render_template('org_admin/build/create_build.html', user=user, org_info=org_info)


@login_required
@org_admin.route('/<org_username>/deploy/<username>', methods=['GET', 'POST'])
def deploy(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    deploy_profiles = mongo.db.profile.find(
        {'$and': [{'username': username}, {'org_username': org_username}, {'type': 'deploy'}]})
    return render_template('org_admin/deploy/index.html', user=user, org_info=org_info, deploy_profiles=deploy_profiles)


@login_required
@org_admin.route('/<org_username>/create_deploy/<username>', methods=['GET', 'POST'])
def create_deploy(username, org_username):
    user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    if request.method == 'POST':
        server_name = request.form['server_name']
        profile_name = request.form['profile_name']
        deploy_username = request.form['deploy_username']
        deploy_password = request.form['deploy_password']
        profile_exist = mongo.db.profile.find_one(
            {'$and': [{'profile_name': profile_name}, {'type': 'deploy'}]})
        if not profile_exist:
            mongo.db.profile.insert({'profile_name': profile_name, 'username': username, 'org_username': org_username,
                                     'type': 'deploy', 'deploy_username': deploy_username, 'deploy_password': deploy_password,
                                     'server_name': server_name})
            return redirect(url_for('org_admin.deploy', username=username, org_username=org_username))
        else:
            print("Profile Already Exists")
    return render_template('org_admin/deploy/create_deploy.html', user=user, org_info=org_info)