

from flask import g
from flask.app import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import Integer, String, Boolean, ForeignKey, UniqueConstraint
import click
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()
migrate = Migrate()

def get_db():
    if 'db' not in g:
        g.db = db

    return g.db

def init_db():
    db.create_all()

@click.command('init-db')
def init_db_command():
    init_db()
    click.echo('Initialized the database.')

def init_app(app : Flask):
    db.init_app(app)
    migrate.init_app(app, db)
    app.cli.add_command(init_db_command)

class user(db.Model):
    __tablename__ = "user"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    email : Mapped[str] = mapped_column(String(100))
    nome : Mapped[str] = mapped_column(String(100))
    cognome : Mapped[str] = mapped_column(String(100))
    classe : Mapped[str] = mapped_column(String(10))
    full_name : Mapped[str] = mapped_column(String(210))
    password : Mapped[str] = mapped_column(String(150))

    iscrizioni = db.relationship('iscrizione', back_populates="user")
    corsi_organizzati = db.relationship('organizza', back_populates="user")
    presenze = db.relationship('presenza', back_populates="user")

    __table_args__ = (
        UniqueConstraint('email', name='uq_user_email'),
    )

    def __init__(self, email : str, nome : str, cognome : str, classe : str, password : str):
        self.email = email
        self.nome = nome
        self.cognome = cognome
        self.classe = classe
        self.full_name = f"{cognome} {nome} {classe}"
        self.password = password


class corso(db.Model):
    __tablename__ = "corso"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    titolo : Mapped[str] = mapped_column(String(200))
    descrizione : Mapped[str] = mapped_column(String(10000))
    posti_totali : Mapped[int] = mapped_column(Integer)
    posti_occupati : Mapped[int] = mapped_column(Integer)
    aula : Mapped[str] = mapped_column(String(100))
    fascia : Mapped[int] = mapped_column(Integer)
    organizzatori_str : Mapped[str] = mapped_column(String(200))
    note : Mapped[str] = mapped_column(String(1000))

    iscrizioni = db.relationship('iscrizione', back_populates="corso")
    organizzatori = db.relationship('organizza', back_populates="corso")
    appello = db.relationship('presenza', back_populates="corso")

    def __init__(self, titolo : str, descrizione : str, posti_totali : int, posti_occupati : int, aula : str, fascia : int, organizzatori_str : str, note : str):
        self.titolo = titolo
        self.descrizione = descrizione
        self.posti_totali = posti_totali
        self.posti_occupati = posti_occupati
        self.aula = aula
        self.fascia = fascia
        self.organizzatori_str = organizzatori_str
        self.note = note


class iscrizione(db.Model):
    __tablename__ = "iscrizione"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id : Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name="fk_user_id"))
    user = db.relationship("user", back_populates="iscrizioni")

    corso_id : Mapped[int] = mapped_column(Integer, ForeignKey('corso.id', name="fk_corso_id"))
    corso = db.relationship("corso", back_populates="iscrizioni")

    def __init__(self, user_id : int, corso_id : int):
        self.user_id = user_id
        self.corso_id = corso_id


class organizza(db.Model):
    __tablename__ = "organizza"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id : Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name="fk_user_id"))
    user = db.relationship("user", back_populates="corsi_organizzati")

    corso_id : Mapped[int] = mapped_column(Integer, ForeignKey('corso.id', name="fk_corso_id"))
    corso = db.relationship("corso", back_populates="organizzatori")

    def __init__(self, user_id : int, corso_id : int):
        self.user_id = user_id
        self.corso_id = corso_id


class presenza(db.Model):
    __tablename__ = "presenza"

    id : Mapped[int] = mapped_column(Integer, primary_key=True)
    presente : Mapped[Boolean] = mapped_column(Boolean)

    user_id : Mapped[int] = mapped_column(Integer, ForeignKey('user.id', name="fk_user_id"))
    user = db.relationship("user", back_populates="presenze")

    corso_id : Mapped[int] = mapped_column(Integer, ForeignKey('corso.id'))
    corso = db.relationship("corso", back_populates="appello")

