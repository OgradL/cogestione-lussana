
from flask import Blueprint, render_template, request, jsonify, json
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
    res = ""

    f = StringIO()
    with redirect_stdout(f):
        try:
            exec(dati["comando"])
            res = f.getvalue().strip()
        except Exception as e:
            res = str(e)

    return jsonify({"res" : res})

