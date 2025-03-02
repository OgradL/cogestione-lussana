
from flask import Flask
from flask import redirect, url_for
from flask import request, jsonify, json
from flask import session
from datetime import timedelta, datetime

orari_fasce = [
	datetime.fromisoformat("2025-04-14T09:00"),
	datetime.fromisoformat("2025-04-14T11:00"),
	datetime.fromisoformat("2025-04-15T09:00"),
	datetime.fromisoformat("2025-04-15T11:00"),
	datetime.fromisoformat("2025-04-16T09:00")
]

def login_required(f):
    def wrapped(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        return redirect(url_for('login', next=request.path.strip("/")))
    wrapped.__name__ = f.__name__
    return wrapped