
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Float, ForeignKey
import main
from os import path


db = SQLAlchemy(main.app)

class user(db.Model):
    id = Column(Integer, primary_key=True)
    fascia1 = Column(Integer, ForeignKey("corso.id"))
    fascia2 = Column(Integer, ForeignKey("corso.id"))
    fascia3 = Column(Integer, ForeignKey("corso.id"))
    fascia4 = Column(Integer, ForeignKey("corso.id"))
    fascia5 = Column(Integer, ForeignKey("corso.id"))



class corso(db.Model):
    id = Column(Integer, primary_key=True)
    titolo = Column(String(100))
    descrizione = Column(String(5000))
    posti_totali = Column(Integer)
    posti_occupati = Column(Integer)
    aula = Column(String(100))
    fascia = Column(Integer)
    utenti = db.relationship("user")

def init_db(app, DB_NAME):
    db.init_app(app)
    if not path.exists(path.join(path.dirname(__file__), "instance", DB_NAME)):
        db.create_all()