
from flask import Blueprint, render_template, request, jsonify, json, redirect, url_for
from io import StringIO
from contextlib import redirect_stdout
from datetime import datetime

from cogestione import utils
from cogestione import db as database
from cogestione.admin_actions import carica_utenti, carica_prof


bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/execute/", methods=["GET", "POST"])
@utils.super_admin_access
def execute():
    if request.method == "GET":
        return render_template("admin.html")

    dati = json.loads(request.data)
    db = database.get_db()

    cmd = ""
    cmd_id = -1

    if "cmd_id" in dati:
        cmd_id = dati["cmd_id"]
    if "comando" in dati:
        cmd = dati["comando"]

    res = ""

    f = StringIO()
    with redirect_stdout(f):
        try:
            exec(cmd)
            res = f.getvalue().strip()
        except Exception as e:
            res = str(e)

    cmd_line = f"{datetime.now().isoformat()} > {cmd}"

    html_format_cmd = f"<span class=\"cmd_line\" onclick=\"recall_cmd({cmd_id})\">{cmd_line}</span>"

    res = html_format_cmd + "<br>" + res
    return jsonify({"res" : res})

@bp.route("/")
def admin():
    return redirect(url_for("admin.execute"))
