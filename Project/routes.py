from flask import Flask, abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from __main__ import app
from __main__ import auth
from models import User, Thread, Comment, Save
from __main__ import db

@app.route('/', methods=['GET'])
def root():
    return "FarmData"


@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('username')
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
def get_username_availabe():
    """Check if username is available."""
    username = request.json.get('username')
    if User.query.filter_by(username=username) is not None:
        return 'available'
    return 'unavailable'


@app.route('/emailavaialble', methods=['POST'])
def get_email_available():
    """Check if email is available."""
    email = request.json.get('email')
    if User.query.filter_by(email=email).first() is not None:
        return 'unavailable'
    return 'available'



@app.route('/getthread', methods=['POST'])
def get_thread():
    """Returns the thread information given the thread id."""
    thread_id = request.json.get('thread_id')
    thread = Thread.query.filter_by(id=int(thread_id)).first()
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
    """Returns the comments given a thread id."""
    thread_id = request.json.get('thread_id')
    comments = Comment.query.filter_by(thread_id=thread_id)
    response = {}
    for comment in comments:
        username = ""
        user = (User.query.filter_by(id=comment.user_id).first())
        if user is not None:
            username = user.username
        response[str(comment.id)] = [comment.description,username]
    return response   


@app.route('/getcreatethread', methods=['POST'])
@auth.login_required
def get_create_thread():
    """Creates a new thread."""
    try:
        title = request.json.get('title')
        description = request.json.get('description')
        username = request.json.get('username')
        if title is None or description is None or username is None:
            return "invalid"
        if title == "" or description == "" or username == "":
            return "invalid"
        user = (User.query.filter_by(username=username).first()).id
        if user is None:
            user = 0
        thread = Thread(title=title,description=description,image_path="",user_id = user)
        db.session.add(thread)
        db.session.commit()
        return str(thread.id)
        # return "hello"
    except:
        return "error"

@app.route('/getcreatecomment', methods=['POST'])
@auth.login_required
def get_create_comment():
    """Creates a new comment."""
    try:
        thread_id = request.json.get('thread_id')
        description = request.json.get('description')
        username = request.json.get('username')
        if description is None or thread_id is None or username is None:
            return "invalid"
        if description == "" or thread_id == "" or username == "":
            return "invalid"
        user = (User.query.filter_by(username=username).first()).id
        if user is None:
            user = 0
        comment = Comment(description=description,image_path="",thread_id=int(thread_id),user_id = user)
        db.session.add(comment)
        db.session.commit()
        return str(comment.id)
        #return "hello"
    except:
        return "error"

maxlen = 100
@app.route('/getthreadlist', methods=['POST'])
@auth.login_required
def get_thread_list():
    """Returns the thread list."""
    try:
        username = request.json.get('username')
        if username is None:
            return "invalid"
        if username == "":
            return "invalid"  
        user = (User.query.filter_by(username=username).first()).id

        ##TODO insert algorithm to create a list of forum posts for the user

        threads = Thread.query.all()
        response = {}
        for thread in threads:
            username = (User.query.filter_by(id=thread.user_id).first()).username
            if username is None:
                username = ""
            response[thread.id] = [thread.title,thread.description[:maxlen],username]
        return response
        #return "hello"
    except:
        return "error"


@app.route('/getsaves', methods=['POST'])
@auth.login_required
def get_saves():
    try:
        username = request.json.get('username')
        if username is None:
            return "invalid"
        if username == "":
            return "invalid"
        user = (User.query.filter_by(username=username).first()).id
        if user is None:
            user = 0

        threads = []
        saves = Save.query.filter_by(user_id = user).all()
        for save in saves:
            if save is not None:
                thread = Thread.query.filter_by(thread_id = save.thread_id).first()
                if thread is not None:
                    threads.append(thread)

        response = {}
        for thread in threads
            username = (User.query.filter_by(id=thread.user_id).first()).username
            if username is None:
                username = ""
            response[str(thread.id)] = [thread.title,thread.description[:maxlen],username]

        return response

    except:
        return 'error'


@app.route('/getsavethread', methods=['POST'])
@auth.login_required
def get_save_thread:
    try:
        username = request.json.get('username')
        thread_id = request.json.get('thread_id')
        if username is None:
            return "invalid"
        if username == "":
            return "invalid"
        user = (User.query.filter_by(username=username).first()).id
        if user is None:
            user = 0
        if thread_id is None:
            return "invalid"
        if thread_id == "":
            return "invalid"
        save = Save(user_id=user,thread_id=int(thread_id))
        db.session.add(save)
        db.session.commit()
        return 'saved'
    except:
        return 'error'

@app.route('/getunsavethread', methods=['POST'])
@auth.login_required
def get_unsave_thread:
    try:
        username = request.json.get('username')
        thread_id = request.json.get('thread_id')
        if username is None:
            return "invalid"
        if username == "":
            return "invalid"
        user_id = (User.query.filter_by(username=username).first()).id
        if user_id is None:
            return 'invalid'
        if thread_id is None:
            return "invalid"
        if thread_id == "":
            return "invalid"
        save = Save.query.filter_by(thread_id=thread_id,user_id=user_id).first()
        db.session.delete(save)
        db.session.commit()
        return 'unsaved'
    except:
        return 'error'


@app.route('/getreport', methods=['POST'])
@auth.login_required
def get_report:
    try:
        username = request.json.get('username')
        if username is None:
            return "invalid"
        if username == "":
            return "invalid"
        user_id = (User.query.filter_by(username=username).first()).id
        if user_id is None:
            return 'invalid'
        #TODO add functionaloty to generate report
        cropResponse = {}
        cropReports = CropReport.query.filter_by(user_id=user_id)
        for cropReport in cropReports:
            cropResponse[cropReport.title] = [cropReport.warning_level,cropReport.description]
        livestockResponse = {}
        livestockReports = LiveStockReport.query.filter_by(user_id=user_id)
        for livestockReport in livestockReports:
            cropResponse[livestockReport.title] = [livestockReport.warning_level,livestockReport.description]
        weatherResponse = {}
        weatherReports = WeatherReport.query.filter_by(user_id=user_id)
        for weatherReport in weatherReports:
            cropResponse[weatherReport.title] = [weatherReport.warning_level,weatherReport.description]
        response = {}
        response['CropReport'] = cropResponse
        response['LiveStockReport'] = livestockReport
        response['WeatherReport'] = weatherReport
        
        return response

    except:
        return 'error'