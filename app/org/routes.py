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
    orgs_names = mongo.db.orgs.find({'name': 1})
    return render_template('org/show_orgs.html', user=user, orgs=orgs, orgs_names=orgs_names)


@login_required
@org.route('/admin/<username>/org/create_org', methods=['GET', 'POST'])
def create_org(username):
    user = mongo.db.users.find_one({'username': username})
    orgs_names = mongo.db.orgs.find({'name': 1})
    if request.method == 'POST':
        print(request)
    return render_template('org/create_org.html', user=user, orgs_names=orgs_names)
