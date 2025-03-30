
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask import request, jsonify, json
from flask import session
from flask import flash
from flask import make_response, Response
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from helper import *
import database
from database import db, app
from io import StringIO
from contextlib import redirect_stdout
import re
from os import path
from werkzeug.security import check_password_hash, generate_password_hash
from xlsxwriter import Workbook
import openpyxl
from random import randint
import requests
import os
import dotenv

DB_NAME = "database.db"
# app = Flask(__name__)
# app.secret_key = "secret key"
# app.permanent_session_lifetime = timedelta(days=7)
# app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'


@app.route("/")
def home():
    return render_template("homepage.html")


@app.route("/admin", methods=["GET", "POST"])
@admin_access
def execute():
    if request.method == "POST":
        
        headers = dict(request.headers)
        dati = json.loads(request.data)
        res = ""
        
        f = StringIO()
        with redirect_stdout(f):
            try:
                exec(dati["comando"])
                res = f.getvalue().strip()
            except:
                res = "error"
        
        # headers["Result"] = str(res)
        return jsonify({"res" : res})
        return Response([b"good"], headers=headers)
    elif request.method == "GET":
        return render_template("admin.html")
    return "idk"

def carica_corsi(path):
    print(path)

    if not os.path.exists(path):
        print("path does not exists")
        return
    
    wb = openpyxl.load_workbook(path)
    ws = wb.active
    values = [ws.cell(row=1,column=i).value for i in range(1,ws.max_column+1)]
    
    print(values)
    
    for value in ws.iter_rows(min_row=2):
        for i in range(1, 6):
            new_corso = database.corso(
                titolo = value[values.find("titolo")].value,
                descrizione = value[values.find("descrizione")].value,
                posti_totali = value[values.find("posti_tatli")].value,
                posti_occupati = 0,
                aula = value[values.find("aula")].value,
                fascia = i,
                organizzatori = value[values.find("organizzatori")].value,
                note = value[values.find("note")].value
            )
            if value[values.find("fascia")].value.find(f"Fascia {i}") != -1:
                # add corso for fascia {i}
                db.session.add(new_corso)
                db.session.commit()
                
    pass

# statistiche

@app.route("/report/", methods=["GET"])
def report():
    dati = {}
    info_classe = {}
    
    sel = db.select(database.iscrizione)
    iscrizioni = db.session.scalars(sel).all()

    sel = db.select(database.user)
    utenti = db.session.scalars(sel).all()
    
    for iscrizione in iscrizioni:
        if iscrizione.userref is None:
            continue
        dati.setdefault(iscrizione.userref.classe, dict())
        dati[iscrizione.userref.classe].setdefault(iscrizione.corsoref.fascia, 0)
        # prev = dati[iscrizione.userref.classe].get(iscrizione.corsoref.fascia)
        # print(dati[iscrizione.userref.classe], " -- ", prev)
        # print(dati["5g"])
        # print(dati)
        dati[iscrizione.userref.classe][iscrizione.corsoref.fascia] += 1
    
    for utente in utenti:
        info_classe.setdefault(utente.classe, 0)
        info_classe[utente.classe] += 1
    
    for classe in dati:
        d = dati[classe]
        # print(classe, d)
        for i in range(1, 6):
            dati[classe].setdefault(i, 0)
            dati[classe][i] = round(dati[classe][i] / info_classe[classe] * 100)
    
    
    
    return render_template("report.html", dati=dati)

def create_xlsx_file(file_path: str, headers: dict, items: list):
    with Workbook(file_path) as workbook:
        worksheet = workbook.add_worksheet()
        worksheet.write_row(row=0, col=0, data=headers.values())
        header_keys = list(headers.keys())
        for index, item in enumerate(items):
            row = map(lambda field_id: item.get(field_id, ''), header_keys)
            worksheet.write_row(row=index + 1, col=0, data=row)

@app.route("/save-data/", methods=["GET"])
def save_data():
    date = str(datetime.now().time())
    date = date[:date.find('.')]
    
    dir_path = path.join('.', "output-data")
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    file_name = path.join('.', "output-data", "dati-" + date + ".xlsx")
    # file_name = "dati-" + date + ".xlsx"
    
    headers = {
        "id" : "Id",
        "nome" : "Nome",
        "cognome" : "Cognome",
        "classe" : "Classe",
        "id_corso" : "Id corso",
        "fascia" : "Fascia",
    }
    
    items = []
    iscrizioni = db.session.scalars(db.select(database.iscrizione)).all()
    
    for iscrizione in iscrizioni:
        if iscrizione.userref is None:
            continue
        items.append({
            "id" : iscrizione.id,
            "nome" : iscrizione.userref.nome,
            "cognome" : iscrizione.userref.cognome,
            "classe" : iscrizione.userref.classe,
            "id_corso" : iscrizione.corsoref.id,
            "fascia" : iscrizione.corsoref.fascia
        })
    
    create_xlsx_file(file_name, headers, items)
    
    return "Done!"

# azioni

@app.route("/lista-corsi/<n_fascia>", methods=["GET"])
def lista_corsi(n_fascia):
    corsi = db.session.execute(db.select(database.corso).filter_by(fascia=n_fascia)).all()
    
    # corsi = database.corso.query.filter_by(id=n_fascia).all()
    corsi = list(map(lambda x : x[0], corsi))
    return render_template("lista-corsi.html", fascia=int(n_fascia), corsi=corsi, dim=len(corsi))

@app.route("/lista-corsi/", methods=["GET"])
def lista_corsi_help():
    return redirect(request.url + "1")

@app.route("/iscrizione/", methods=["POST"])
@login_required
def iscrizione():
    dati = json.loads(request.data)
    id_corso = dati["id_corso"]
    
    user = db.session.execute(db.select(database.user).filter_by(email=session["email"])).first()[0]
    corso = db.session.execute(db.select(database.corso).filter_by(id=id_corso)).first()[0]
    
    if corso is None:
        flash("Il corso non esiste", 'error')
        return Response([b"error"], 400)
    
    if corso.posti_occupati == corso.posti_totali:
        flash("Il corso è pieno!", 'error')
        return Response([b"error"], 400)
    
    # iscrizioni = db.session.execute(db.select(database.iscrizione).filter_by())
    # print(user)
    # print(user[0].iscrizioni)
    # iscrizioni = user.iscrizioni

    sel = db.select(database.iscrizione).join(database.user).where(database.user.email == session["email"])
    iscrizioni = db.session.scalars(sel).all()
    
    sel = db.select(database.organizza).join(database.user).where(database.user.email == session["email"])
    organizzazioni = db.session.scalars(sel).all()
    # iscrizioni = db.session.scalars(db.select(database.iscrizione).where(database.iscrizione.userref.email == session["email"])).all()
    
    #(db.select(database.user, database.iscrizione, database.corso).filter_by(email=session["email"])).all()

    # print(iscrizioni)
    
    for iscrizione in iscrizioni:
        if iscrizione.corsoref.fascia == corso.fascia:
            flash("Sei già iscritto a un corso per questa fascia. Puoi annullare l'iscrizione dal tuo profilo", 'error')
            return Response([b"error"], 400)

    for organizza in organizzazioni:
        if organizza.corsoref.fascia == corso.fascia:
            flash("Sei già organizzatore di un corso per questa fascia", 'error')
            return Response([b"error"], 400)
    
    
    # print("iscritto a", id_corso)
    db.session.add(database.iscrizione(utente=user.id, corso=corso.id))
    corso.posti_occupati += 1
    db.session.commit()
    
    flash("Iscritto con successo", 'success')
    return Response([b"good"], 200)

@app.route("/annulla-iscrizione/", methods=["POST"])
@login_required
def annulla_iscrizione():
    dati = json.loads(request.data)
    id_corso = dati["id_corso"]
    
    corso = db.session.execute(db.select(database.corso).filter_by(id=id_corso)).first()[0]
    sel = db.select(database.iscrizione).join(database.user).join(database.corso).where(database.user.email == session["email"], database.corso.id == id_corso)
    iscrizione = db.session.scalars(sel).first()
    
    if iscrizione is None:
        return Response([b"bad"], 404)
    
    db.session.delete(iscrizione)
    corso.posti_occupati -= 1
    db.session.commit()
    
    return jsonify({})

@app.route("/corso/<id_corso>", methods=["GET"])
def info_corso(id_corso):
    corso = database.corso.query.filter_by(id=id_corso).first()
    return render_template("corso.html", corso=corso)

# profilo

@app.route("/profile/")
@login_required
def profile():
    
    user = db.session.execute(db.select(database.user).filter_by(email=session["email"])).first()[0]
    
    sel = db.select(database.iscrizione).join(database.user).where(database.user.email == session["email"])
    iscrizioni = db.session.scalars(sel).all()
    
    sel = db.select(database.organizza).join(database.user).where(database.user.email == session["email"])
    organizzazioni = db.session.scalars(sel).all()
    
    corsi = [dict() for _ in range(6)]
    
    for iscrizione in iscrizioni:
        d = corsi[iscrizione.corsoref.fascia]
        d["id"] = iscrizione.corsoref.id
        d["titolo"] = iscrizione.corsoref.titolo
        d["posti"] = f"{iscrizione.corsoref.posti_occupati} / {iscrizione.corsoref.posti_totali}"
        d["organizzatori"] = iscrizione.corsoref.organizzatori_str
        d["aula"] = iscrizione.corsoref.aula
        d["organizzato"] = False
        # d["annulla iscrizione"] = f"<button onclick=\"annulla_iscrizione({iscrizione.corsoref.id})\"> Annulla </button>"
    
    for organizza in organizzazioni:
        d = corsi[organizza.corsoref.fascia]
        d["id"] = organizza.corsoref.id
        d["titolo"] = organizza.corsoref.titolo
        d["posti"] = f"{organizza.corsoref.posti_occupati} / {organizza.corsoref.posti_totali}"
        d["organizzatori"] = organizza.corsoref.organizzatori_str
        d["aula"] = organizza.corsoref.aula
        d["organizzato"] = True
    
    
    return render_template("profile.html", corsi=corsi, utente=user, orari_fasce=orari_fasce)

# accesso al profilo
@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    email = request.form.get("email")
    password = request.form.get("password")
    
    user = db.session.execute(db.select(database.user).filter_by(email=email)).first()
    
    if user is None:
        flash("Email o password errati", 'error')
        return render_template("login.html")
    
    if not check_password_hash(user[0].password, password):
    # if user[0].password != password:
        flash("Email o password errati", 'error')
        return render_template("login.html")

    session["email"] = email
    session["logged"] = True
    
    flash("Login effettuato con successo", 'success')
    return redirect(url_for("lista_corsi", n_fascia=1))

def send_email(to_email, subject, content):
    dotenv.load_dotenv()
    res = requests.post(
        "https://api.eu.mailgun.net/v3/cogestione-lussana.eu/messages",
        auth=("api", os.getenv('API_KEY', 'API_KEY')),
        data={"from": "Iscrizioni Cogestione Lussana <iscrizioni@cogestione-lussana.eu>",
            "to": to_email,
            "subject": subject,
            "text": content
            })
    
    # print(to_email, res)

def send_auth_verification_email(email):
    testo = f"""Questo è il tuo codice di verififca:\n\t{session["auth_code"]}\n\nInseriscilo nella pagina di registrazione!"""
    
    send_email(email,
               "Codice di verifica cogestione",
               testo)

def send_pwd_reset_email(email):
    testo = f"""Questo è il tuo codice di verifica:\n\t{session["auth_code"]}\n\nInseriscilo nella pagina di reset della password!"""
    
    send_email(email, "Codice di verifica cogestione", testo)


@app.route("/verification/", methods=["GET", "POST"])
def verification():
    if session.get("auth_code", -1) == -1 or session.get("auth_age", -1) == -1:
        return redirect(url_for("home"))
    
    if (datetime.now() - datetime.fromisoformat(session["auth_age"])).seconds >= 600:
        session.clear()
    
    if session.get("auth_code", -1) == -1 or session.get("auth_age", -1) == -1:
        return redirect(url_for("home"))
    
    
    if request.method == "GET":
        return render_template("verification.html")
    
    code = request.form.get("verification-code")
    
    if code != session["auth_code"]:
        session.clear()
        flash("Il codice di controllo è sbagliato", 'error')
        return redirect(url_for("register"))
    
    # user = session["user"]
    email = session["tmp_email"]
    nome = session["tmp_nome"]
    cognome = session["tmp_cognome"]
    classe = session["tmp_classe"]
    password = session["tmp_password"]
    session.clear()
    
    user = database.user(email=email, nome=nome, cognome=cognome, classe=classe, password=password)
    db.session.add(user)
    db.session.commit()
    
    flash("Registrato con successo", 'success')
    return redirect(url_for("login"))

@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    failed = False
    
    nome = request.form.get("name")
    cognome = request.form.get("lastname")
    email = request.form.get("email")
    classe = request.form.get("classe")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
    
    if re.match(EMAIL_REGEX, email) is None:
        flash("Email non valida", 'error')
        failed = True

    if not email.endswith("@liceolussana.eu"):
        flash("Devi usare l'email istituzionale (...@liceolussana.eu)")
        failed = True
    
    classe = sanitize_classe(classe)
    
    if classe is None or False:
        flash("La classe non è valida", 'error')
        failed = True
    
    # more checks
    
    user = db.session.execute(db.select(database.user).filter_by(email=email)).first()
    
    if user is not None:
        flash("L'email è già usata", "error")
        failed = True
    
    if password1 != password2:
        flash("Le password non corrispondono", 'error')
        failed = True

    if failed:
        return render_template("register.html")
    
    session.clear()
    session["auth_code"] = "".join([str(randint(0, 9)) for _ in range(6)])
    session["auth_code"] = "000000"
    session["auth_age"] = datetime.now().isoformat()
    
    flash(f"Ti abbiamo inviato una mail di verifica su {email}")
    
    # send_auth_verification_email(email)
    
    password = generate_password_hash(password1)

    session["tmp_email"] = email
    session["tmp_nome"] = nome
    session["tmp_cognome"] = cognome
    session["tmp_classe"] = classe
    session["tmp_password"] = password

    return redirect(url_for("verification"))

@app.route("/verification-reset-pwd/", methods=["GET", "POST"])
def verification_reset_pwd():
    if session.get("auth_code", -1) == -1 or session.get("auth_age", -1) == -1:
        return redirect(url_for("home"))
    
    if (datetime.now() - datetime.fromisoformat(session["auth_age"])).seconds >= 600:
        session.clear()
    
    if session.get("auth_code", -1) == -1 or session.get("auth_age", -1) == -1:
        return redirect(url_for("home"))
    
    
    if request.method == "GET":
        return render_template("verification-reset-pwd.html")
    
    code = request.form.get("verification-code")
    
    if code != session["auth_code"]:
        session.clear()
        flash("Il codice di controllo è sbagliato", 'error')
        return redirect(url_for("reset_password"))
    
    email = session["tmp_email"]
    password = session["tmp_password"]
    session.clear()
    
    user = db.session.execute(db.select(database.user).filter_by(email=email)).first()[0]
    print(user)
    print(password)
    user.password = password
    db.session.commit()
    
    flash("Password modificata con successo", 'success')
    return redirect(url_for("login"))

@app.route("/reset-password/", methods=["GET", "POST"])
def reset_password():
    if request.method == "GET":
        return render_template("reset-pwd.html")
    
    failed = False
    
    email = request.form.get("email")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")
    
    # more checks
    
    user = db.session.execute(db.select(database.user).filter_by(email=email)).first()
    
    if user is None:
        flash("L'email non è valida", "error")
        failed = True
    
    if password1 != password2:
        flash("Le password non corrispondono", 'error')
        failed = True

    if failed:
        return render_template("reset-pwd.html")
    
    session.clear()
    session["auth_code"] = "".join([str(randint(0, 9)) for _ in range(6)])
    session["auth_age"] = datetime.now().isoformat()
    
    flash(f"Ti abbiamo inviato una mail di verifica su {email}")
    
    send_pwd_reset_email(email)
    
    password = generate_password_hash(password1)
    
    session["tmp_email"] = email
    session["tmp_password"] = password

    return redirect(url_for("verification_reset_pwd"))

@app.route("/logout/")
@login_required
def logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    dotenv.load_dotenv()
    
    corsitmp = [
        database.corso(
            titolo="prova corsoo",
            descrizione="descrizione bella",
            posti_totali=50,
            posti_occupati=20,
            aula="Ed. 2, Piano 1, aula 36",
            fascia="1",
            organizzatori_str="persona 1",
            note="nota 1"
        ),
        database.corso(
            titolo="corso serio",
            descrizione="black jack",
            posti_totali=5,
            posti_occupati=1,
            aula="Ed. 2, Piano 2, aula 32",
            fascia="2",
            organizzatori_str="beccia",
            note="wooof"
        ),
        database.corso(
            titolo="corso brutto",
            descrizione="descrizione brutta ma molto lunga lungalunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lunglunga lungaaaaaaaaaaaaaaaaaaaaaa",
            posti_totali=10,
            posti_occupati=0,
            aula="Ed. 2, Piano 1, aula 36",
            fascia="1",
            organizzatori_str="ferry",
            note="tosta"
        ),
        database.corso(
            titolo="corso cp",
            descrizione="ds + dp + grafi + advanced techincs",
            posti_totali=150,
            posti_occupati=149,
            aula="Ed. 2, Piano 0, Laboratorio Ravasio",
            fascia="1",
            organizzatori_str="drago",
            note="tanta cp bella"
        )
    ]
    
    with app.app_context():
        # db.drop_all()
        # db.init_app(app)
        # db.create_all()
        database.init_db(app)
        
        for corso in corsitmp:
            q = db.session.execute(db.select(database.corso).filter_by(id=corso.id)).first()
            if q is None:
                db.session.add(corso)
                db.session.commit()
        
        app.run(debug=True)
