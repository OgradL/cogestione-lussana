
from flask import redirect, url_for, flash
from flask import session
from random import randint
import os

from cogestione import db as database

EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""

orari_fasce = [
    "",
    "30/03 - 08:10",
    "30/03 - 09:45",
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

def riassegna_aule():
    db = database.get_db()
    aule = db.session.scalars(db.select(database.aula).order_by(database.aula.posti_totali.desc())).all()
    for fascia in range(1, 6):
        corsi = db.session.scalars(db.select(database.corso).where(database.corso.fascia == fascia).order_by(database.corso.posti_occupati.desc())).all()
        aule_fissate = []

        for c in corsi:
            if c.aula_fissata:
                aule_fissate.append(c.aula_id)

        idx_aule = 0
        for c in corsi:
            if idx_aule >= len(aule):
                break
            if c.aula_fissata or aule[idx_aule].id in aule_fissate:
                continue
            c.aula_id = aule[idx_aule].id
            # c.aula = aule[idx_aule].nome
            c.posti_totali = aule[idx_aule].posti_totali
            idx_aule += 1
        db.session.commit()
