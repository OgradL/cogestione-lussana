
from flask import Flask
from flask import redirect, url_for
from flask import request, jsonify, json
from flask import session

def login_required(f):
    def wrapped(*args, **kwargs):
        print(session.items())
        if 'email' in session:
            return f(*args, **kwargs)
        return redirect(url_for('login', next=request.path.strip("/")))
    wrapped.__name__ = f.__name__
    return wrapped