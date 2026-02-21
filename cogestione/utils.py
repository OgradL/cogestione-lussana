
from flask import redirect, url_for, flash
from flask import session
from random import randint
import os

EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

orari_fasce = [
    "",
    "30/03 - 09:45",
    "30/03 - 11:30",
    "31/03 - 09:45",
    "31/03 - 11:30",
    "1/04 - 09:30",
]

def is_loggin(f):
    def wrapped(*args, **kwargs):
        if "loggin_in" in session and session["loggin_in"]:
            return f(*args, **kwargs)
        return redirect(url_for('auth.prelogin'))
    wrapped.__name__ = f.__name__
    return wrapped


def login_required(f):
    def wrapped(*args, **kwargs):
        if "logged" in session and session["logged"]:
            return f(*args, **kwargs)
        flash("Devi aver fatto il login!", 'error')
        return redirect(url_for('auth.login'))
    wrapped.__name__ = f.__name__
    return wrapped

def is_admin(email):
    return email in os.getenv("admin_emails") or is_super_admin(email)

def is_super_admin(email):
    return email in os.getenv("super_admin_emails")

def admin_access(f):
    def wrapped(*args, **kwargs):
        if 'email' in session:
            if is_admin(session['email']):
                return f(*args, **kwargs)
        return redirect(url_for('core.home'))
    wrapped.__name__ = f.__name__
    return wrapped

def super_admin_access(f):
    def wrapped(*args, **kwargs):
        if 'email' in session:
            if is_super_admin(session['email']):
                return f(*args, **kwargs)
        return redirect(url_for('core.home'))
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

def generate_auth_code(len : int = 6):
    return "".join([str(randint(0, 9)) for _ in range(len)])
