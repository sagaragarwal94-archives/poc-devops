from flask import render_template, request, redirect, url_for
from flask_login import login_user, login_required, current_user
from app.org import org
from app import mongo, bcrypt, login_manager
from app.user.user_loging_manager import User


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
            mongo.db.orgs.insert({'name': org_name, 'username': org_username, 'desc': org_description, 'image': org_image, 'org_admins': '', 'status': 'active'})
            return redirect(url_for('org.show_orgs', username=user['username']))
    return render_template('org/create_org.html', user=user, orgs_names=orgs_names)


@login_required
@org.route('/admin/<username>/org/edit_org/<org_username>', methods=['GET', 'POST'])
def edit_org(username, org_username):
    user = mongo.db.users.find_one({'username': username})
    orgs_names = mongo.db.orgs.find({}, {'name': 1, 'username': 1})
    org_info = mongo.db.orgs.find_one({'username': org_username})
    return render_template('org/edit_org.html', user=user, org_info=org_info, orgs_names=orgs_names)


@login_required
@org.route('/admin/<username>/org/delete/<org_username>', methods=['GET'])
def delete_org(username, org_username):
    mongo.db.orgs.delete_one({'username': org_username})
    return redirect(url_for('org.show_orgs', username=username))


@login_required
@org.route('/admin/<username>/org/status/<org_username>', methods=['GET'])
def org_status(username, org_username):
    org_info = mongo.db.orgs.find_one({'username': org_username})
    if org_info['status'] == 'active':
        mongo.db.orgs.update_one({'username': org_username}, {'$set': {'status': 'suspend'}})
    else:
        mongo.db.orgs.update_one({'username': org_username}, {'$set': {'status': 'active'}})
    return redirect(url_for('org.edit_org', username=username, org_username=org_username))