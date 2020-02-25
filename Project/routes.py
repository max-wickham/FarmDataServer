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



@app.route('/getreport', methods=['POST'])
@auth.login_required
def get_report:
    """Returns the report list"""
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