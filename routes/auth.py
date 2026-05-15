import os
import hmac
from flask import Blueprint, request, session, redirect, url_for, render_template

auth_bp = Blueprint("auth", __name__)

APP_LOGIN_USERNAME = os.environ.get("APP_LOGIN_USERNAME", "admin")
APP_LOGIN_PASSWORD = os.environ.get("APP_LOGIN_PASSWORD", "")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if not os.environ.get("APP_LOGIN_PASSWORD"):
        return redirect(url_for("main.index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        valid = hmac.compare_digest(username, APP_LOGIN_USERNAME) and hmac.compare_digest(
            password, APP_LOGIN_PASSWORD
        )
        if valid:
            session["authenticated"] = True
            return redirect(url_for("main.index"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
