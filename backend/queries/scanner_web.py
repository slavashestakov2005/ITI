from flask import render_template

from backend import app


@app.route("/scanner", methods=["GET"])
def scanner_page():
    return render_template("scanner.html")
