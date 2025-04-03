
from flask import Flask
from flask import redirect, url_for, flash
from flask import request, jsonify, json
from flask import session
from datetime import timedelta, datetime

EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

orari_fasce = [
    "",
    "14/04 - 09:45",
    "14/04 - 11:30",
    "15/04 - 09:45",
    "15/04 - 11:30",
    "16/04 - 09:30",
]

admin_emails = [
    "drago.leonardo.studente@liceolussana.eu"
]

def login_required(f):
    def wrapped(*args, **kwargs):
        if 'email' in session:
            return f(*args, **kwargs)
        flash("Devi aver fatto il login!", 'error')
        return redirect(url_for('login'))
    wrapped.__name__ = f.__name__
    return wrapped

def admin_access(f):
    def wrapped(*args, **kwargs):
        if 'email' in session:
            if session['email'] in admin_emails:
                return f(*args, **kwargs)
        return redirect(url_for('home'))
    wrapped.__name__ = f.__name__
    return wrapped

def sanitize_classe(classe : str):
    num, sez = '', ''
    for c in classe:
        if c.isalpha():
            sez += c.upper()
        elif c.isnumeric():
            num += c
    if len(num) == 1 and len(sez) == 1:
        return num + sez.upper()
    return None