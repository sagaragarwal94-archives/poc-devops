from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_required
from app.org import org
from app import mongo


@login_required
@org.route('/admin/<username>/org', methods=['GET'])
def show_orgs(username):
    user = mongo.db.users.find_one({'username': username})
    orgs = mongo.db.orgs.find({})
    orgs_names = mongo.db.orgs.find({}, {'name': 1, 'username': 1})
    return render_template('org/show_orgs.html', user=user, orgs=orgs, orgs_names=orgs_names)


@login_required
@org.route('/admin/<username>/org/create_org', methods=['GET', 'POST'])
def create_org(username):
    user = mongo.db.users.find_one({'username': username})
    orgs_names = mongo.db.orgs.find({}, {'name': 1, 'username': 1})
    # orgs_admins = mongo.db.users.find({'$and':[{'org_name': org_name},{'role':'org_admin'}]})
    if request.method == 'POST':
        org_name = request.form['orgname']
        org_username = request.form['orgusername']
        org_description = request.form['orgdescription']
        org_image = request.form['orgimage']
        exist_status = mongo.db.orgs.find_one({'username': org_username})
        if exist_status:
            print("Username exists, create a different organisation")
        else:
            mongo.db.orgs.insert(
                {'name': org_name, 'username': org_username, 'desc': org_description, 'image': org_image,
                 'org_admins': '', 'status': 'active'})
            return redirect(url_for('org.show_orgs', username=user['username']))
    return render_template('org/create_org.html', user=user, orgs_names=orgs_names)


@login_required
@org.route('/admin/<username>/org/edit_org/<org_username>', methods=['GET', 'POST'])
def edit_org(username, org_username):
    user = mongo.db.users.find_one({'username': username})
    orgs_names = mongo.db.orgs.find({}, {'name': 1, 'username': 1})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    org_admins = mongo.db.users.find({'$and': [{'role': 'orgadmin'}, {'org_username': org_username}]})
    return render_template('org/edit_org.html', user=user, org_info=org_info, orgs_names=orgs_names,
                           org_admins=org_admins)


@login_required
@org.route('/admin/<username>/org/delete/<org_username>', methods=['GET'])
def delete_org(username, org_username):
    mongo.db.orgs.delete_one({'username': org_username})
    mongo.db.users.delete_many({'org_username': org_username})
    return redirect(url_for('org.show_orgs', username=username))


@login_required
@org.route('/admin/<username>/org/status/<org_username>', methods=['GET'])
def org_status(username, org_username):
    org_info = mongo.db.orgs.find_one({'username': org_username})
    admin_usernames = mongo.db.users.find({'org_username': org_username}, {'username': 1, '_id': 0})
    names_list = []
    for admin_username in admin_usernames:
        names_list.append(admin_username['username'])
    if org_info['status'] == 'active':
        mongo.db.orgs.update_one({'username': org_username}, {'$set': {'status': 'suspend'}})
        mongo.db.users.update_many({'username': {'$in': names_list}}, {'$set': {'status': 'suspend'}})

    else:
        mongo.db.orgs.update_one({'username': org_username}, {'$set': {'status': 'active'}})
        mongo.db.users.update_many({'username': {'$in': names_list}}, {'$set': {'status': 'active'}})
    return redirect(url_for('org.edit_org', username=username, org_username=org_username))


@login_required
@org.route('/admin/org/create_org_admin', methods=['GET'])
def create_org_admin():
    data = request.args
    name = data.to_dict()['name']
    username = data.to_dict()['username']
    password = data.to_dict()['password']
    repassword = data.to_dict()['repassword']
    org_username = data.to_dict()['org_username']
    org_info = mongo.db.orgs.find_one({'username': org_username}, {'org_admins': 1, '_id': 0})
    org_admins = org_info['org_admins'].split(',')
    if password == repassword:
        exist_user = mongo.db.users.find_one({'$and': [{'username': username}, {'org_username': org_username}]})
        if exist_user:
            return jsonify({'code': 'User of username exists, different Username', 'status': 405})
        else:
            mongo.db.users.insert(
                {'name': name, 'username': username, 'password': password, 'role': 'orgadmin', 'status': 'active',
                 'org_username': org_username})
            org_admins.append(username)
            mongo.db.orgs.update_one({'username': org_username}, {'$set': {'org_admins': ",".join(org_admins)}})
            return jsonify({'code': 'User created', 'status': 200})
    else:
        return jsonify({'code': 'Password never matched', 'status': 405})


@login_required
@org.route('/admin/org/edit_org_admin', methods=['GET'])
def edit_org_admin():
    data = request.args
    username = data.to_dict()['username']
    password = data.to_dict()['password']
    mongo.db.users.update_one({'username': username}, {'$set': {'password': password}})
    return jsonify({'code': 'Password Changed for {username}'.format(username=username)})


@login_required
@org.route('/admin/org/status_org_admin', methods=['GET'])
def status_org_admin():
    data = request.args
    username = data.to_dict()['username']
    status = data.to_dict()['status']
    org_username = data.to_dict()['org_username']
    admin_username = data.to_dict()['admin_username']
    if status == 'active':
        mongo.db.users.update_one({'username': username}, {'$set': {'status': 'suspend'}})
        return jsonify({'url': '/admin/{admin_username}/org/edit_org/{org_username}'.format(
            admin_username=admin_username, org_username=org_username)})

    else:
        mongo.db.users.update_one({'username': username}, {'$set': {'status': 'active'}})
        return jsonify({'url': '/admin/{admin_username}/org/edit_org/{org_username}'.format(
            admin_username=admin_username, org_username=org_username)})


@login_required
@org.route('/admin/org/delete_org_admin', methods=['GET'])
def delete_org_admin():
    data = request.args
    username = data.to_dict()['username']
    org_username = data.to_dict()['org_username']
    admin_username = data.to_dict()['admin_username']
    mongo.db.users.delete_one({'username': username})
    org_info = mongo.db.orgs.find_one({'username': org_username}, {'org_admins': 1, '_id': 0})
    org_admins = org_info['org_admins'].split(',')
    org_admins.remove(username)
    mongo.db.orgs.update_one({'username': org_username}, {'$set': {'org_admins': ",".join(org_admins)}})
    return jsonify({'url': '/admin/{admin_username}/org/edit_org/{org_username}'.format(admin_username=admin_username,
                                                                                        org_username=org_username)})
