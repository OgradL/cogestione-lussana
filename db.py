
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Float, ForeignKey
from app import app


db = SQLAlchemy(app)

class user(db.Model):
    id = Column(Integer, primary_key=True)
    fascia1 = Column(Integer)
    fascia2 = Column(Integer)
    fascia3 = Column(Integer)
    fascia4 = Column(Integer)
    fascia5 = Column(Integer)
    fascia6 = Column(Integer)


class corso(db.Model):
    id = Column(Integer, primary_key=True)
    descrizione = Column(String(5000))
    posti = Column(Integer)
    aula = Column(String(100))

