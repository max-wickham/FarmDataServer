import os
import base64
import boto3
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

from exts import application
from exts import auth
#Create Config Class
class ConfigClass(object):
    """ Flask application config """
    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'    # File-based SQL database
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://farmdata:asdr5tgn4b@farmdata.c8ax3wfehkfa.us-east-2.rds.amazonaws.com/farmdata_database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning
    
# Create Flask app load app.config
#application = Flask(__name__)
#application.config.from_object(__name__+'.ConfigClass')

from exts import db;
# Initialize Flask-SQLAlchemy
#db = SQLAlchemy(application)
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://farmdata:asdr5tgn4b@farmdata.c8ax3wfehkfa.us-east-2.rds.amazonaws.com/farmdata_database'
#app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

#Initialize Auth
#from exts import auth
#auth = HTTPBasicAuth()

from models import User, Thread, Comment, Save
#import routes
#import forum_routes
#import authentication
#from authentication import authenticate

db.init_app(application)
db.create_all()

if __name__ == "__main__":
    application.run(host = "0.0.0.0")
    #app.run(debug=True)

###########################################
#####Routes###############################
#########################################
def verify(username, password):
    return True
    # first try to authenticate by token
    user = User.query.filter_by(username=username).first()
    if user:
        if user.verify_password(password):
            return True
    return False




@application.route('/', methods=['GET'])
def root():
    return "farm" #len(pwd_context.encrypt("FarmData"))


@application.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    email = request.json.get('email')
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
    db.session.close()
    #db.session.rollback()
    return 'added user'



@application.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return 'missing_username_or_password'    #missing arguments
    if not verify(username,password):
        return "Unauthorised"
    user = User.query.filter_by(username=username).first()
    return "logged in"

@application.route('/profile')
def get_resource():
    return 'username:'


@application.route('/usernameavailable', methods=['POST'])
def get_username_availabe():
    """Check if username is available."""
    username = request.json.get('username')
    if User.query.filter_by(username=username) is not None:
        return 'available'
    return 'unavailable'


@application.route('/emailavailable', methods=['POST'])
def get_email_available():
    """Check if email is available."""
    email = request.json.get('email')
    if User.query.filter_by(email=email).first() is not None:
        return 'unavailable'
    return 'available'



###########################################
#####Forum Routes#########################
#########################################

@application.route('/getthread', methods=['POST'])
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
    return "error"

@application.route('/getcomments', methods=['POST'])
def get_comments():
    """Returns the comments given a thread id."""
    try:
        thread_id = request.json.get('thread_id')
        comments = Comment.query.filter_by(thread_id=int(thread_id))
        response = {}
        for comment in comments:
            username = ""
            user = (User.query.filter_by(id=comment.user_id).first())
            if user is not None:
                username = user.username
            response[str(comment.id)] = {"description":comment.description,"username":username}
        return response   
    except:
        return 'invalid'



@application.route('/getcreatethread', methods=['POST'])
def get_create_thread():
    """Creates a new thread."""
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return 'missing_username_or_password'    #missing arguments
        if not verify(username,password):
            return "Unauthorised"
        title = request.json.get('title')
        description = request.json.get('description')
        imagestring = request.json.get('image')
        imagetype = request.json.get('imagetype')
        #file = request.files["image"]
        if title is None or description is None or username is None:
            return "invalid1"
        if title == "" or description == "" or username == "":
            return "invalid2"
        user = (User.query.filter_by(username=username).first()).id
        if user is None:
            user = 0
        thread = Thread(title=title,description=description,image_path="",user_id = user)
        db.session.add(thread)
        db.session.flush()
        path = ''
        if imagestring is not None and imagetype is not None:
            imgdata = base64.b64decode(imagestring)
            filename = 'threadimage' + str(thread.id) + imagetype 
            try:
                session = boto3.Session(region_name='us-west-2')#profile_name="dev")#, aws_access_key_id = 'AKIAIES54JJCF725MAMA', aws_secret_access_key = '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')
                s3 = session.resource('s3')
                s3.Bucket('farmdataimages').put_object(Body = imgdata,Key = filename, ACL='public-read')
                path = 'https://farmdataimages.s3-us-west-2.amazonaws.com/' + filename
            except:
                path = ''
        thread.image_path = path
        db.session.commit()
        db.session.close()
        return "posted"
        # return "hello"
    except:
        return "invalid3"

@application.route('/getcreatecomment', methods=['POST'])
def get_create_comment():
    """Creates a new comment."""
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return 'missing_username_or_password'    #missing arguments
        if not verify(username,password):
            return "Unauthorised"
        thread_id = request.json.get('thread_id')
        description = request.json.get('description')
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
        db.session.close()
        return "posted"
        #return "hello"
    except:
        return "error"

maxlen = 100 #maximum length of forum description in list form
@application.route('/getthreadlist', methods=['POST'])
def get_thread_list():
    """Returns the thread list."""
    try:
        #return "test"
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return 'missing_username_or_password'    #missing arguments
        if not verify(username,password):
            return "Unauthorised" 
        #return "test"
        user_id = (User.query.filter_by(username=username).first()).id
        
        ##TODO insert algorithm to create a list of forum posts for the user

        threads = Thread.query.all()
        response = {}
        for thread in threads:
            username = (User.query.filter_by(id=thread.user_id).first()).username
            if username is None:
                username = ""
            response[thread.id] = {"title":thread.title,"description":thread.description[:maxlen],"username":username,"image":thread.image_path}
        if response == {}:
            return "empty"
        #return "hello"
        return response
    except:
        return "invalid"


@application.route('/getsaves', methods=['POST'])
def get_saves():
    """Returns the saves given the username"""
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return 'missing_username_or_password'    #missing arguments
        if not verify(username,password):
            return "Unauthorised"
        user = (User.query.filter_by(username=username).first()).id
        if user is None:
            user = 0
        threads = []
        saves = Save.query.filter_by(user_id = user).all()
        for save in saves:
            if save is not None:
                thread = Thread.query.filter_by(id = save.thread_id).first()
                if thread is not None:
                    threads.append(thread)
  

        response = {}
        for thread in threads:
            username = (User.query.filter_by(id=thread.user_id).first()).username
            if username is None:
                username = ""
            response[thread.id] = {"title":thread.title,"description":thread.description[:maxlen],"username":username}
        #response = "hello"
        return response

    except:
        return 'invalid'


@application.route('/getsavethread', methods=['POST'])
def get_save_thread():
    """Saves a new thread given thread id and username"""
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return 'missing_username_or_password'    #missing arguments
        if not verify(username,password):
            return "Unauthorised"
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
        db.session.close()
        return 'saved'
    except:
        return 'invalid'

@application.route('/getunsavethread', methods=['POST'])
def get_unsave_thread():
    """unsaves a thread given thread id and username"""
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return 'missing_username_or_password'    #missing arguments
        if not verify(username,password):
            return "Unauthorised"
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
        return 'invalid'

@application.route('/getsearchlist', methods=['POST'])
def get_search_list():
    try:
        search = request.json.get('search')
        username = request.json.get('username')
        password = request.json.get('password')
        if username is None or password is None:
            return 'missing_username_or_password'    #missing arguments
        if not verify(username,password):
            return "Unauthorised"
        if username is None:
            return "invalid"
        if username == "":
            return "invalid"  
        user_id = (User.query.filter_by(username=username).first()).id


        return 'unimplemented'

    except:
        return 'invalid'
