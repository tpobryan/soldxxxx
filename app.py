import os
import hmac
import secrets
from markupsafe import Markup
from flask import Flask, session, request, abort, redirect, url_for
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(32))

AUTH_ENABLED = bool(os.environ.get("APP_LOGIN_PASSWORD", ""))
APP_LOGIN_USERNAME = os.environ.get("APP_LOGIN_USERNAME", "admin")
APP_LOGIN_PASSWORD = os.environ.get("APP_LOGIN_PASSWORD", "")


def get_csrf_token():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def validate_csrf_token(token):
    expected = session.get("csrf_token", "")
    return hmac.compare_digest(expected, token or "")


@app.before_request
def csrf_protect():
    if request.method != "POST":
        return
    if request.endpoint in ("auth.login", "healthz"):
        return
    if not validate_csrf_token(request.form.get("csrf_token", "")):
        abort(403)


@app.before_request
def require_auth():
    if not AUTH_ENABLED:
        return
    if session.get("authenticated"):
        return
    allowed = {"auth.login", "auth.logout", "healthz", "static"}
    if request.endpoint in allowed:
        return
    return redirect(url_for("auth.login"))


@app.context_processor
def inject_globals():
    csrf_val = get_csrf_token()
    return dict(
        auth_enabled=AUTH_ENABLED,
        is_authenticated=session.get("authenticated", False),
        csrf_token=csrf_val,
        csrf_input=Markup(
            f'<input type="hidden" name="csrf_token" value="{csrf_val}">'
        ),
    )


@app.route("/healthz")
def healthz():
    return "ok", 200


from routes.auth import auth_bp  # noqa: E402
from routes.main import main_bp  # noqa: E402

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=False)
