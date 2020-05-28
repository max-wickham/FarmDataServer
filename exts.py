import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from flask_httpauth import HTTPBasicAuth

class ConfigClass(object):
    """ Flask application config """
    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///basic_app.sqlite'    # File-based SQL database
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://farmdata:asdr5tgn4b@farmdata.c8ax3wfehkfa.us-east-2.rds.amazonaws.com/farmdata_database'
    SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids SQLAlchemy warning
    
application  = Flask(__name__)
application.config.from_object(__name__+'.ConfigClass')
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://farmdata:asdr5tgn4b@farmdata.c8ax3wfehkfa.us-east-2.rds.amazonaws.com/farmdata_database'
db = SQLAlchemy(application)
auth = HTTPBasicAuth()