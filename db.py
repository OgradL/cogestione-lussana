
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Float, ForeignKey
import app


db = SQLAlchemy(app.app)

class user(db.Model):
    id = Column(Integer, primary_key=True)
    fascia1 = Column(Integer, ForeignKey("corso.id"))
    fascia2 = Column(Integer, ForeignKey("corso.id"))
    fascia3 = Column(Integer, ForeignKey("corso.id"))
    fascia4 = Column(Integer, ForeignKey("corso.id"))
    fascia5 = Column(Integer, ForeignKey("corso.id"))



class corso(db.Model):
    id = Column(Integer, primary_key=True)
    descrizione = Column(String(5000))
    posti_totali = Column(Integer)
    posti_occupati = Column(Integer)
    aula = Column(String(100))
    fascia = Column(Integer)

