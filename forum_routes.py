from flask import Flask, abort, request, jsonify, g, url_for
from flask_httpauth import HTTPBasicAuth
from exts import application
from exts import auth
from models import User, Thread, Comment, Save
from exts import db

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
    return "error"

@app.route('/getcomments', methods=['POST'])
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

@app.route('/getcreatethread', methods=['POST'])
@auth.login_required
def get_create_thread():
    """Creates a new thread."""
    try:
        title = request.json.get('title')
        description = request.json.get('description')
        file = request.files["image"]
        username = auth.username()
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
        return "posted"
        # return "hello"
    except:
        return "invalid"

@app.route('/getcreatecomment', methods=['POST'])
@auth.login_required
def get_create_comment():
    """Creates a new comment."""
    try:
        thread_id = request.json.get('thread_id')
        description = request.json.get('description')
        username = auth.username()
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
        return "posted"
        #return "hello"
    except:
        return "error"

maxlen = 100 #maximum length of forum description in list form
@app.route('/getthreadlist', methods=['POST'])
@auth.login_required
def get_thread_list():
    """Returns the thread list."""
    try:
        username = auth.username()
        if username is None:
            return "invalid"
        if username == "":
            return "invalid"  
        user_id = (User.query.filter_by(username=username).first()).id

        ##TODO insert algorithm to create a list of forum posts for the user

        threads = Thread.query.all()
        response = {}
        for thread in threads:
            username = (User.query.filter_by(id=thread.user_id).first()).username
            if username is None:
                username = ""
            response[thread.id] = {"title":thread.title,"description":thread.description[:maxlen],"username":username}
        return response
        #return "hello"
    except:
        return "invalid"


@app.route('/getsaves', methods=['POST'])
@auth.login_required
def get_saves():
    """Returns the saves given the username"""
    try:
        username = auth.username()
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


@app.route('/getsavethread', methods=['POST'])
@auth.login_required
def get_save_thread():
    """Saves a new thread given thread id and username"""
    try:
        username = auth.username()
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
        return 'invalid'

@app.route('/getunsavethread', methods=['POST'])
@auth.login_required
def get_unsave_thread():
    """unsaves a thread given thread id and username"""
    try:
        username = auth.username()
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

@app.route('/getsearchlist', methods=['POST'])
@auth.login_required
def get_search_list():
    try:
        search = request.json.get('search')
        username = auth.username()
        if username is None:
            return "invalid"
        if username == "":
            return "invalid"  
        user_id = (User.query.filter_by(username=username).first()).id


        return 'unimplemented'

    except:
        return 'invalid'
