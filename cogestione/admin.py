
from flask import Blueprint, render_template, request, jsonify, json, redirect, url_for
from io import StringIO
from contextlib import redirect_stdout

from cogestione import utils
from cogestione import db as database


bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route("/execute/", methods=["GET", "POST"])
@utils.admin_access
def execute():
    if request.method == "GET":
        return render_template("admin.html")

    dati = json.loads(request.data)

    cmd = ""
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

    return jsonify({"res" : res})

@bp.route("/")
def admin():
    return redirect(url_for("admin.execute"))
