
from flask import Flask
from flask import redirect, url_for, flash
from flask import request, jsonify, json
from flask import session
from datetime import timedelta, datetime

EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

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
        flash("Devi aver fatto il login!", 'error')
        return redirect(url_for('login', next=request.path.strip("/")))
    wrapped.__name__ = f.__name__
    return wrapped