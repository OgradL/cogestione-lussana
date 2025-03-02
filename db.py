
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Float, ForeignKey
import app


db = SQLAlchemy(app.app)

class user(db.Model):
    id = Column(Integer, primary_key=True)
    fascia1 = Column(Integer)
    fascia2 = Column(Integer)
    fascia3 = Column(Integer)
    fascia4 = Column(Integer)
    fascia5 = Column(Integer)



class corso(db.Model):
    id = Column(Integer, primary_key=True)
    descrizione = Column(String(5000))
    posti_totali = Column(Integer)
    posti_occupati = Column(Integer)
    aula = Column(String(100))
    fascia = Column(Integer)

