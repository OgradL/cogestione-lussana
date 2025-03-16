
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Float, ForeignKey
import main
from os import path


db = SQLAlchemy(main.app)

class user(db.Model):
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True)
    nome = Column(String(50))
    cognome = Column(String(50))
    classe = Column(String(2))
    password = Column(String(50))
    iscrizioni = db.relationship('iscrizione')


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
    iscrizioni = db.relationship('iscrizione')


class iscrizione(db.Model):
    id = Column(Integer, primary_key=True)
    utente = Column(Integer, ForeignKey('user.id'))
    corso = Column(Integer, ForeignKey('corso.id'))


def init_db(app, DB_NAME):
    db.init_app(app)
    if not path.exists(path.join(path.dirname(__file__), "instance", DB_NAME)):
        db.create_all()