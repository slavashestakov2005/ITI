from flask import render_template
from flask_login import login_required

from backend import app
from .help import check_access
from ..help import UserRoleLogin


@app.route("/scanner_barcode", methods=["GET"])
@login_required
@check_access(roles=[UserRoleLogin.LOGIN_LOCAL])
def scanner_barcode():
    return render_template("scanner_barcode.html")
