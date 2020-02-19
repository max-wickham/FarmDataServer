from flask import Flask, abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from __main__ import db
from enum import Enum



class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    email = db.Column(db.String(64), index = True)
    password_hash = db.Column(db.String(64))
    verified = db.Column(db.Boolean)
    #threads written by the user links to threads table
    threads = db.relationship('Thread', backref='author', lazy='dynamic')
    #reports for the user
    weather_reports = db.relationship('WeatherReports', backref='user', lazy='dynamic')
    livestock_reports = db.relationship('LiveStockReport', backref='user', lazy='dynamic')
    crop_reports = db.relationship('CropReport', backref='user', lazy='dynamic')
    #farminfo profile information for the user
    farminfo_livestocks = db.relationship('FarmInfoLiveStock', backref='user', lazy='dynamic')
    farminfo_lcrops = db.relationship('FarmInfoCrop', backref='user', lazy='dynamic')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    #def generate_report(self):
        ##TODO

    #def generate_threads(self):



class Thread(db.Model):
    __tablename__ = 'threads'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), index=True)
    description = db.Column(db.String(1000), index=True)
    image_path = db.Column(db.String(32), index=True)
    #timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    posts = db.relationship('Comment', backref='thread', lazy='dynamic')



class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(1000), index=True)
    image_path = db.Column(db.String(32), index=True)
    #timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('threads.id'))



class WeatherReport(db.Model):
    __tablename__ = 'weather_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(64), index=True)
    #timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    warning_level = db.Column(db.Integer, index = True) #Warning level from 0 to 10
    description = db.Column(db.String(240), index=True)
    


class LiveStockReport(db.Model):
    __tablename__ = 'livestock_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(64), index=True)
    #timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    warning_level = db.Column(db.Integer, index = True) #Warning level from 0 to 10
    description = db.Column(db.String(240), index=True)

class CropReport(db.Model):
    __tablename__ = 'crop_reports'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    title = db.Column(db.String(64), index=True)
    #timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    warning_level = db.Column(db.Integer, index = True) #Warning level from 0 to 10
    description = db.Column(db.String(240), index=True)


class FarmInfoLiveStock(db.Model):
    __tablename__ = 'farminfo_livestocks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    livestock = db.Column(db.String(32), index=True)
    size = db.Column(db.Integer, index = True) #size in km^2
    latitude = db.Column(db.Integer, index = True)
    longitude = db.Column(db.Integer, index = True)

class FarmInfoCrop(db.Model): 
    __tablename__ = 'farminfo_crops'   
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    crop = db.Column(db.String(32), index=True)
    size = db.Column(db.Integer, index = True) #size in km^2
    latitude = db.Column(db.Integer, index = True)
    longitude = db.Column(db.Integer, index = True)