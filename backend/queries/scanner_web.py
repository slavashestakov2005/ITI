from flask import redirect, render_template, request, session

from backend import app
from ..config import Config


def scanner_authed() -> bool:
    return session.get("scanner_admin") is True


@app.route("/scanner/login", methods=["GET", "POST"])
def scanner_login():
    if scanner_authed():
        return redirect("/scanner")
    error = None
    if request.method == "POST":
        login = (request.form.get("login") or "").strip()
        password = request.form.get("password") or ""
        if login == Config.SCANNER_ADMIN_LOGIN and password == Config.SCANNER_ADMIN_PASSWORD:
            session["scanner_admin"] = True
            return redirect("/scanner")
        error = "Неверный логин или пароль"
    return render_template("scanner_login.html", error=error)


@app.route("/scanner/logout", methods=["GET"])
def scanner_logout():
    session.pop("scanner_admin", None)
    return redirect("/scanner/login")


@app.route("/scanner", methods=["GET"])
def scanner_page():
    if not scanner_authed():
        return redirect("/scanner/login")
    return render_template("scanner.html")
