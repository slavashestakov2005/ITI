from flask import render_template
from flask_login import login_required

from backend import app
from .help import check_access
from ..help import UserRoleLogin


#0 -> result 
#1 -> barcode

@app.route("/scanner_result", methods=["GET"])
@login_required
@check_access(roles=[UserRoleLogin.LOGIN_LOCAL])
def scanner_result():
    return render_template("scanner_web.html", x = 0)



@app.route("/scanner_barcode", methods=["GET"])
@login_required
@check_access(roles=[UserRoleLogin.LOGIN_LOCAL])
def scanner_barcode():
    return render_template("scanner_web.html", x = 1)
