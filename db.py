
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, Float, ForeignKey
import main
from os import path


db = SQLAlchemy(main.app)

class user(db.Model):
    id = Column(Integer, primary_key=True)
    fascia1 = Column(Integer)
    fascia2 = Column(Integer)
    fascia3 = Column(Integer)
    fascia4 = Column(Integer)
    fascia5 = Column(Integer)



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

def init_db(app, DB_NAME):
    db.init_app(app)
    if not path.exists(path.join(path.dirname(__file__), "instance", DB_NAME)):
        db.create_all()