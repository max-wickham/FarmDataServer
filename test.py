#import os
#from flask import Flask, abort, request, jsonify, g, url_for
#from flask_sqlalchemy import SQLAlchemy
#from flask_httpauth import HTTPBasicAuth
#from passlib.apps import custom_app_context as pwd_context
#from werkzeug.security import generate_password_hash, check_password_hash
#from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
#from models import User
#name = pwd_context.encrypt("FarmData")
#print(generate_password_hash("FarmData"))
#print(check_password_hash(generate_password_hash("FarmData"),"FarmData"))
#user = User(username=max,email=max,verified=True)
#user.hash_password("123456")
#print(user.verify_password("123456"))

import boto3

session = boto3.Session(profile_name="dev", aws_access_key_id = 'AKIAIES54JJCF725MAMA', aws_secret_access_key = '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')

#s3 = session.client('s3')
#buckets = s3.list_buckets()
s3 = session.resource('s3')
key = 'test2s3.txt'
s3.Bucket('farmdataimages').put_object(Body = 'test.txt',Key = key, ACL='public-read')
#s3.upload_file('test.txt','farmdataimages',key, ACL='public-read')
endpoint = 'https://farmdataimages.s3-us-west-2.amazonaws.com/'
url = endpoint + key
print(url)
#for bucket in buckets['Buckets']:

#    print (bucket['CreationDate'].ctime(), bucket['Name'])

import base64
imgdata = base64.b64decode("test")
filename = 'some_image.txt'  # I assume you have a way of picking unique filenames
with open(filename, 'wb') as f:
    f.write(str(len("test")))
    f.close()