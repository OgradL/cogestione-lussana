
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Float, ForeignKey
from datetime import timedelta, datetime
# from main import app
from os import path

DB_NAME = "database.db"
app = Flask("__main__", template_folder=path.join(path.dirname(__file__), 'templates'))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
app.permanent_session_lifetime = timedelta(days=7)
app.secret_key = "secret key"
db = SQLAlchemy(app)

class user(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    nome = Column(String(50))
    cognome = Column(String(50))
    classe = Column(String(2))
    password = Column(String(150))
    iscrizioni = db.relationship('iscrizione', backref="userref", lazy=True)


class corso(db.Model):
    id = Column(Integer, primary_key=True)
    titolo = Column(String(100))
    descrizione = Column(String(5000))
    posti_totali = Column(Integer)
    posti_occupati = Column(Integer)
    aula = Column(String(100))
    fascia = Column(Integer)
    organizzatori = Column(String(200))
    note = Column(String(1000))
    iscrizioni = db.relationship('iscrizione', backref="corsoref", lazy=True)


class iscrizione(db.Model):
    id = Column(Integer, primary_key=True)
    utente = Column(Integer, ForeignKey('user.id'))
    corso = Column(Integer, ForeignKey('corso.id'))


def init_db(app):
    # db.init_app(app)
    if not path.exists(path.join(path.dirname(__file__), "instance", DB_NAME)):
        db.create_all()