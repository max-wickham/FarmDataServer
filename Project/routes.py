from flask import Flask, abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from __main__ import app
from __main__ import auth
from models import User
from __main__ import db

@app.route('/', methods=['GET'])
def root():
    return "FarmData"


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = reques.json.get('username')
    password = request.json.get('password')
    if username is None or password is None or email is None:
        return 'missing username or password'    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        return 'existing_user'   # existing user
    if User.query.filter_by(email=email).first() is not None:
        return 'existing_email'   # existing user
    user = User(username=username,email=email,verified=True)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return 'added_user'

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return 'missing_username_or_password'    # missing arguments
    user = User.query.filter_by(username=username).first()
    if user is not None:
        if user.verify_password(password):
            return 'logged in'
        return 'password_incorrect'
    return 'no_user_found'



@app.route('/profile')
@auth.login_required
def get_resource():
    return 'username:' + auth.username()


@app.route('/usernameavailable', methods=['POST'])
def get_username_avaialbe():
    username = request.json.get('username')
    if User.query.filter_by(username=username) is not None:
        return 'available'
    return 'unavailable'


@app.route('/emailavaialble', methods=['POST'])
def ge_email_available():
    email = request.json.get('email')
    if User.query.filter_by(email=email).first() is not None:
        return 'unavailable'
    return 'available'



@app.route('/getthread', methods=['POST'])
def get_thread():
    id = request.json.get('id')
    thread = Thread.query.filter_by(id=id).first()
    if thread is not None:
        user = (User.query.filter_by(id=thread.user_id).first()).username
        if user is None:
            user = ""
        
        response = {
            'title':thread.title,
            'description':thread.description,
            'image_path':thread.image_path,
            'user':user,
        }
        return response

@app.route('/getcomments', methods=['POST'])
def get_comments():
    id = request.json.get('id')
    comments = Comment.query.filter_by(thread_id=id)
    for comment in comments:
        user = (User.query.filter_by(id=comment.user_id).first()).username
        if user is None:
            user = ""
        response[str(comment.id)] = [comment.description,comment.imagepath,user]
    return response   