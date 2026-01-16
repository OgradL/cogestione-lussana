
from flask import Blueprint, Response, render_template, flash, redirect, url_for, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import requests
import os


from cogestione import utils
from cogestione import db as database


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route("/prelogin/", methods=["GET", "POST"])
def prelogin():
    flashes = session.get("_flashes", [])
    session.clear()
    session["_flashes"] = flashes

    if request.method == "GET":
        return render_template("prelogin.html")

    db = database.get_db()
    email = request.form.get("email")

    if email is None:
        return Response("bad request", 400)

    email = email.strip()

    user = db.session.scalar(db.select(database.user).filter_by(email=email))

    if user is None:
        flash("Email non esistente. Se si tratta di un errore, contatta i rappresentanti", 'error')
        return redirect(url_for("auth.prelogin"))

    session.permanent = True
    session["loggin_in"] = True
    session["email"] = email

    if user.password == "":
        return redirect(url_for("auth.register"))

    return redirect(url_for("auth.login"))

@bp.route("/login/", methods=["GET", "POST"])
@utils.is_loggin
def login():
    if request.method == "GET":
        return render_template("login.html", user_email = session["email"])

    db = database.get_db()

    # email = request.form.get("email")
    email = session["email"]
    password = request.form.get("password")

    if email is None or password is None:
        return Response("bad request", 400)

    email = email.strip()
    password = password.strip()

    user = db.session.scalar(db.select(database.user).where(database.user.email == email))

    if user is None:
        flash("Email o password errati", 'error')
        return redirect(url_for("auth.login"))

    if not check_password_hash(user.password, password):
        flash("Email o password errati", 'error')
        return redirect(url_for("auth.login"))

    session.clear()
    session.permanent = True
    session["user_id"] = user.id
    session["email"] = email
    session["logged"] = True

    flash("Login effettuato con successo", 'success')
    return redirect(url_for("core.home"))


def send_email(to_email, subject, content):
    local_api_key = os.getenv("LOCAL_API_KEY")
    relay_url = os.getenv("RELAY_URL")

    from_email = "iscrizioni@cogestione-lussana.eu"

    os.makedirs("logs/", exist_ok=True)
    with open("logs/log.txt", "+a") as f:
        f.writelines(f"""{datetime.now().isoformat()}:
\tFrom: {from_email}
\tTo: {to_email}
\tSubject: {subject}
\tContent: {content}

----------------------------------------------
""")

    if local_api_key is None or relay_url is None:
        return

    res = requests.post(
        relay_url,
        json={"api_key": local_api_key,
              "from_email": from_email,
              "to_email": to_email,
              "subject": subject,
              "content": content
              }
    )

    return res

def send_auth_verification_email(email):
    testo = f"""Questo è il tuo codice di verififca:\n\t{session["auth_code"]}\n\nInseriscilo nella pagina di registrazione!"""

    send_email(email,
               "Codice di verifica cogestione",
               testo)

def send_pwd_reset_email(email):
    testo = f"""Questo è il tuo codice di verifica:\n\t{session["auth_code"]}\n\nInseriscilo nella pagina di reset della password!"""

    send_email(email, "Codice di verifica cogestione", testo)


@bp.route("/verification/", methods=["GET", "POST"])
def verification():
    if session.get("auth_code", -1) == -1 or session.get("auth_age", -1) == -1:
        return redirect(url_for("core.home"))

    if (datetime.now() - datetime.fromisoformat(session["auth_age"])).seconds >= 600:
        session.clear()

    if session.get("auth_code", -1) == -1 or session.get("auth_age", -1) == -1:
        return redirect(url_for("core.home"))


    if request.method == "GET":
        return render_template("verification.html")

    db = database.get_db()

    code = request.form.get("verification-code")

    if code is None:
        return Response("bad request", 400)

    code = code.strip()

    if code != session["auth_code"]:
        session.clear()
        flash("Il codice di controllo è sbagliato", 'error')
        return redirect(url_for("auth.register"))

    email = session["tmp_email"]
    password = session["tmp_password"]
    session.clear()

    user = db.session.scalar(db.select(database.user).filter_by(email=email))
    user.password = password

    db.session.commit()

    flash("Registrato con successo", 'success')
    return redirect(url_for("auth.prelogin"))

@bp.route("/register/", methods=["GET", "POST"])
@utils.is_loggin
def register():
    if request.method == "GET":
        return render_template("register.html", user_email = session["email"])

    failed = False

    db = database.get_db()

    # email = request.form.get("email")
    email = session["email"]
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    if email is None or password1 is None or password2 is None:
        return Response("bad request", 400)

    email = email.strip()
    password1 = password1.strip()
    password2 = password2.strip()

    if not email.endswith("@liceolussana.eu"):
        flash("Devi usare l'email istituzionale (...@liceolussana.eu)")
        failed = True


    # more checks

    user = db.session.scalar(db.select(database.user).where(database.user.email == email))

    if user is None:
        flash("L'email non è esistente. Se credi ci sia stato un errore, contatta i rappresentanti", "error")
        failed = True
        return redirect(url_for("auth.register"))

    if user.password != "":
        flash("L'email è già registrata", 'error')

    if password1 != password2:
        flash("Le password non corrispondono", 'error')
        failed = True

    if failed:
        return redirect(url_for("auth.register"))

    session.clear()
    session["auth_code"] = utils.generate_auth_code(6)
    session["auth_age"] = datetime.now().isoformat()

    flash(f"Ti abbiamo inviato una mail di verifica su {email}")

    send_auth_verification_email(email)

    password = generate_password_hash(password1)

    session["tmp_email"] = email
    session["tmp_password"] = password

    return redirect(url_for("auth.verification"))


@bp.route("/verification-reset-pwd/", methods=["GET", "POST"])
def verification_reset_pwd():
    if session.get("auth_code", -1) == -1 or session.get("auth_age", -1) == -1:
        return redirect(url_for("core.home"))

    if (datetime.now() - datetime.fromisoformat(session["auth_age"])).seconds >= 600:
        session.clear()

    if session.get("auth_code", -1) == -1 or session.get("auth_age", -1) == -1:
        return redirect(url_for("core.home"))


    if request.method == "GET":
        return render_template("verification-reset-pwd.html")

    db = database.get_db()

    code = request.form.get("verification-code")

    if code is None:
        return Response("bad request", 400)

    code = code.strip()

    if code != session["auth_code"]:
        session.clear()
        flash("Il codice di controllo è sbagliato", 'error')
        return redirect(url_for("auth.reset_password"))

    email = session["tmp_email"]
    password = session["tmp_password"]
    session.clear()

    user = db.session.scalar(db.select(database.user).filter_by(email=email))

    user.password = password
    db.session.commit()

    session.clear()

    flash("Password modificata con successo", 'success')
    return redirect(url_for("auth.prelogin"))

@bp.route("/reset-password/", methods=["GET", "POST"])
@utils.is_loggin
def reset_password():
    if request.method == "GET":
        return render_template("reset-pwd.html", user_email=session["email"])

    failed = False

    db = database.get_db()

    email = session["email"]
    # email = request.form.get("email")
    password1 = request.form.get("password1")
    password2 = request.form.get("password2")

    if email is None or password1 is None or password2 is None:
        return Response("bad request", 400)

    email = email.strip()
    password1 = password1.strip()
    password2 = password2.strip()

    # more checks

    user = db.session.scalar(db.select(database.user).filter_by(email=email))

    if user is None:
        flash("L'email non è valida", "error")
        failed = True

    if password1 != password2:
        flash("Le password non corrispondono", 'error')
        failed = True

    if failed:
        return redirect(url_for("auth.reset-password"))

    session.clear()
    session["auth_code"] = utils.generate_auth_code(6)
    session["auth_age"] = datetime.now().isoformat()

    flash(f"Ti abbiamo inviato una mail di verifica su {email}")

    send_pwd_reset_email(email)

    password = generate_password_hash(password1)

    session["tmp_email"] = email
    session["tmp_password"] = password

    return redirect(url_for("auth.verification_reset_pwd"))

@bp.route("/logout/")
@utils.login_required
def logout():
    session.clear()
    return redirect(url_for("core.home"))

