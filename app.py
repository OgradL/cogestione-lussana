
from flask import Flask
from flask import redirect, url_for
from flask import render_template
from flask import request, jsonify, json
from flask import session
from flask import make_response, Response
from datetime import timedelta, datetime
from flask_sqlalchemy import SQLAlchemy
from helper import *


app = Flask(__name__)
app.secret_key = "secret key"
app.permanent_session_lifetime = timedelta(days=7)

@app.route("/")
def home():
    return render_template("homepage.html")


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
    app.run(debug=True)
