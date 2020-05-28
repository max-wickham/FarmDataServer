from flask import Flask, abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from exts import application
from exts import auth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from models import User


@auth.verify_password
def verify_password(username, password):
    # first try to authenticate by token
    user = User.query.filter_by(username=username).first()
    if user:
        if user.verify_password(password):
            return True
    return False

