
from flask import Blueprint, Response, flash, jsonify, render_template, redirect, request, session, url_for
from flask import json

from cogestione import utils
from cogestione import db as database

bp = Blueprint('core', __name__, url_prefix='/')

@bp.route("/")
def home():
    return render_template("homepage.html")

@bp.route("/lista-corsi/<n_fascia>", methods=["GET"])
def lista_corsi(n_fascia):
    try:
        n_fascia = int(n_fascia)
    except ValueError:
        return redirect(url_for("core.home"))

    n_fascia = min(n_fascia, 5)
    n_fascia = max(n_fascia, 1)

    db = database.get_db()

    corsi = db.session.scalars(db.select(database.corso).filter_by(fascia=n_fascia)).all()
    
    return render_template("lista-corsi.html", fascia=int(n_fascia), corsi=corsi, dim=len(corsi))

@bp.route("/lista-corsi/", methods=["GET"])
def lista_corsi_help():
    return redirect(request.url + "1")

@bp.route("/iscrizione/", methods=["POST"])
@utils.login_required
def iscrizione():

    db = database.get_db()

    dati = json.loads(request.data)
    id_corso = dati["id_corso"]
    
    user = db.session.scalar(db.select(database.user).filter_by(id=session["user_id"]))
    corso = db.session.scalar(db.select(database.corso).filter_by(id=id_corso))
    
    if corso is None:
        flash("Il corso non esiste", 'error')
        return Response("Corso inesistente", 400)
    
    if corso.posti_occupati == corso.posti_totali:
        flash("Il corso è pieno!", 'error')
        return Response("Corso pieno", 403)
    


    sel = db.select(database.iscrizione).join(database.user).where(database.user.id == session["user_id"])
    iscrizioni = db.session.scalars(sel).all()
    
    sel = db.select(database.organizza).join(database.user).where(database.user.id == session["user_id"])
    organizzazioni = db.session.scalars(sel).all()


    if any(list(map(lambda x : x.corso.fascia == corso.fascia, iscrizioni))):
        flash("Sei già iscritto a un corso per questa fascia. Puoi annullare l'iscrizione dal tuo profilo", 'error')
        return Response("Già iscritto", 403)

    if any(list(map(lambda x : x.corso.fascia == corso.fascia, organizzazioni))):
        flash("Sei già organizzatore per un corso di questa fascia. Puoi annullare l'iscrizione dal tuo profilo", 'error')
        return Response("Già organizzatore", 403)
    

    db.session.add(database.iscrizione(user_id=user.id, corso_id=corso.id))
    corso.posti_occupati += 1
    db.session.commit()
    
    flash("Iscritto con successo", 'success')
    return Response("Iscritto con successo", 200)

@bp.route("/annulla-iscrizione/", methods=["POST"])
@utils.login_required
def annulla_iscrizione():

    db = database.get_db()

    dati = json.loads(request.data)
    id_corso = dati["id_corso"]
    
    corso = db.session.scalar(db.select(database.corso).filter_by(id=id_corso))

    sel = db.select(database.iscrizione).join(database.user).join(database.corso).where(database.user.id == session["user_id"], database.corso.id == id_corso)
    iscrizione = db.session.scalar(sel)
    
    if iscrizione is None:
        return Response([b"Iscrizione inesistente"], 404)
    
    db.session.delete(iscrizione)
    corso.posti_occupati -= 1
    db.session.commit()
    
    return Response("Iscrizione rimossa", 200)

@bp.route("/corso/<id_corso>", methods=["GET"])
def info_corso(id_corso):

    db = database.get_db()

    corso = db.session.scalar(db.select(database.corso).filter_by(id=id_corso))

    referenti = " - ".join(list(map(lambda x : f"{x.user.nome} {x.user.cognome} {x.user.classe}", corso.organizzatori)))

    return render_template("corso.html", corso=corso, referenti=referenti)


@bp.route("/create-corso/", methods=["GET", "POST"])
@utils.login_required
def create_corso():
    if request.method == "GET":
        return render_template("create-corso.html")

    db = database.get_db()

    titolo = request.form.get("titolo")
    descrizione = request.form.get("descrizione")
    organizzatori = request.form.get("organizzatori")
    note = request.form.get("note")

    fascia1 = request.form.get("fascia1")
    fascia2 = request.form.get("fascia2")
    fascia3 = request.form.get("fascia3")
    fascia4 = request.form.get("fascia4")
    fascia5 = request.form.get("fascia5")

    if titolo is None or descrizione is None or organizzatori is None:
        return Response("bad request", 400)

    if note is None:
        note = ""

    fasce = [fascia1, fascia2, fascia3, fascia4, fascia5]

    fasce = [i+1 for i, el in enumerate(fasce) if el]

    if len(fasce) == 0:
        flash("Non è stata scelta nessuna fascia")
        return redirect(url_for("core.create-corso"))

    for f in fasce:
        corso = database.corso(titolo, descrizione, 30, 0, "tbd", f, organizzatori, note)

        db.session.add(corso)

    db.session.commit()

    flash("Corso creato con successo!", "success")
    return redirect(url_for("core.profile"))

@bp.route("/get_students/<query>", methods=["GET"])
def get_students(query : str):


    db = database.get_db()

    query = query.replace(" ", "%")
    query = "%" + query + "%"

    users = db.session.scalars(db.select(database.user).where(database.user.full_name.ilike(query)).limit(10)).all()

    return jsonify([
        {"id" : user.id, "email" : user.email, "full_name" : user.full_name} for user in users
    ])


# profilo

@bp.route("/profile/", methods=["GET"])
@utils.login_required
def profile():

    db = database.get_db()
    
    user = db.session.scalar(db.select(database.user).filter_by(email=session["email"]))
    

    sel = db.select(database.iscrizione).join(database.user).where(database.user.id == session["user_id"])
    iscrizioni = db.session.scalars(sel).all()
    
    sel = db.select(database.organizza).join(database.user).where(database.user.id == session["user_id"])
    organizzazioni = db.session.scalars(sel).all()


    corsi = [dict() for _ in range(6)]


    for iscrizione in iscrizioni:
        isc_corso = iscrizione.corso
        d = corsi[isc_corso.fascia]

        d["id"] = isc_corso.id
        d["titolo"] = isc_corso.titolo
        d["posti"] = f"{isc_corso.posti_occupati} / {isc_corso.posti_totali}"
        d["organizzatori"] = " - ".join(list(map(lambda x : f"{x.user.nome} {x.user.cognome} {x.user.classe}", isc_corso.organizzatori)))
        d["aula"] = isc_corso.aula
        d["organizzato"] = False
        d["annulla iscrizione"] = f"<button onclick=\"annulla_iscrizione({isc_corso.id})\"> Annulla </button>"
    
    for organizza in organizzazioni:
        org_corso = organizza.corso
        d = corsi[org_corso.fascia]

        d["id"] = org_corso.id
        d["titolo"] = org_corso.titolo
        d["posti"] = f"{org_corso.posti_occupati} / {org_corso.posti_totali}"
        d["organizzatori"] = " - ".join(list(map(lambda x : f"{x.user.nome} {x.user.cognome} {x.user.classe}", org_corso.organizzatori)))
        d["aula"] = org_corso.aula
        d["organizzato"] = True
    
    
    return render_template("profile.html", corsi=corsi, utente=user)

