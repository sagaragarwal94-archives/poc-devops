from flask import render_template, request, redirect, url_for
from flask_login import login_user, login_required, current_user
from app.admin import admin
from app import mongo, bcrypt, login_manager
from app.user.user_loging_manager import User


@login_required
@admin.route('/admin/<username>', methods=['POST', 'GET'])
def profile(username):
    user = mongo.db.users.find_one({'username': username})
    if request.method == 'POST':
        oldpassword = request.form['oldPassword']
        newpassword = request.form['newPassword']
        recheckpassword = request.form['renewPassword']
        if oldpassword == user['password']:
            if newpassword == recheckpassword:
                mongo.db.users.update_one({'username': username}, {'$set': {'password': newpassword}}, upsert=False)
                return redirect(url_for('user.logout'))
            else:
                print('password mismatch')
        else:
            print('existing password fail')
    return render_template('admin/profile.html', user=user)


@login_required
@admin.route('/admin/<username>/show_admins', methods=['GET'])
def show_admins(username):
    user = mongo.db.users.find_one({'username': username})
    admins_details = mongo.db.users.find({'username': {'$ne': username}})
    admins_names = mongo.db.users.find({'username': {'$ne': username}}, {'name': 1, 'username': 1})
    return render_template('admin/show_admins.html', user=user, admins_details=admins_details, admins_names=admins_names)


@login_required
@admin.route('/admin/<username>/create_admin', methods=['GET', 'POST'])
def create_admin(username):
    user = mongo.db.users.find_one({'username': username})
    admins_details = mongo.db.users.find({'username': {'$ne': username}})
    admins_names = mongo.db.users.find({'username': {'$ne': username}}, {'name': 1, 'username': 1})
    if request.method == 'POST':
        new_name = request.form['name']
        new_username = request.form['username']
        new_password = request.form['password']
        new_repassword = request.form['repassword']
        if new_password == new_repassword:
            exist_user = mongo.db.users.find_one({'username': new_username})
            if exist_user:
                print('User already exists')
            else:
                mongo.db.users.insert({'name': new_name, 'username': new_username,
                                       'password': new_password, 'status': 'active',
                                       'role': 'admin'})
        else:
            print('password mismatch')
        return redirect(url_for('admin.profile', username=user['username']))
    return render_template('admin/create_admin.html', user=username, admins_details=admins_details, admins_names=admins_names)


@login_required
@admin.route('/admin/<username>/other_admin/<other_admin_username>', methods=['GET', 'POST'])
def edit_other_admin(username, other_admin_username):
    user = mongo.db.users.find_one({'username': username})
    other_admin = mongo.db.users.find_one({'username': other_admin_username})
    admins_names = mongo.db.users.find({'username': {'$ne': username}}, {'name': 1, 'username': 1})
    if request.method == 'POST':
        new_password = request.form['newpassword']
        re_new_password = request.form['re_newpassword']
        if new_password == re_new_password:
            mongo.db.users.update_one({'username': other_admin['username']}, {'$set': {'password': new_password}}, upsert=False)
            return redirect(url_for('admin.show_admins', username=user['username']))
        else:
            print("password mismatch")
    return render_template('admin/edit_other_admin.html', user=user, other_admin=other_admin, admins_names=admins_names)


@login_required
@admin.route('/admin/<username>/other_admin/<other_admin_username>/delete', methods=['GET'])
def delete_other_admin(username, other_admin_username):
    user = mongo.db.users.find_one({'username': username})
    mongo.db.users.delete_one({'username': other_admin_username})
    return redirect(url_for('admin.show_admins', username=user['username']))


@login_required
@admin.route('/admin/<username>/other_admin/<other_admin_username>/<status>', methods=['GET'])
def other_admin_status(username, other_admin_username, status):
    user = mongo.db.users.find_one({'username': username})
    other_admin = mongo.db.users.find_one({'username': other_admin_username})
    if status == 'active':
        mongo.db.users.update_one({'username': other_admin['username']}, {'$set': {'status': 'suspend'}}, upsert=False)
        return redirect(url_for('admin.edit_other_admin', username=user['username'], other_admin_username=other_admin['username']))
    else:
        mongo.db.users.update_one({'username': other_admin['username']}, {'$set': {'status': 'active'}}, upsert=False)
        return redirect(
            url_for('admin.edit_other_admin', username=user['username'], other_admin_username=other_admin['username']))
