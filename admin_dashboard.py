
import os
import hmac
from functools import wraps

from flask import (
    Flask, render_template, jsonify, request, redirect,
    url_for, session, abort
)
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from database import get_connection

app = Flask(__name__)

app.config.update(
    SECRET_KEY=os.environ.get("JANSAARTHI_SECRET_KEY"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    WTF_CSRF_TIME_LIMIT=3600,
)

ADMIN_USERNAME = os.environ.get("JANSAARTHI_ADMIN_USERNAME", "")
ADMIN_PASSWORD_HASH = os.environ.get("JANSAARTHI_ADMIN_PASSWORD_HASH", "")

# Refuse to start if essential security settings are missing.
if not app.config["SECRET_KEY"]:
    raise RuntimeError("Set JANSAARTHI_SECRET_KEY before starting the admin app.")

if len(app.config["SECRET_KEY"]) < 32:
    raise RuntimeError("JANSAARTHI_SECRET_KEY must be at least 32 characters.")

if not ADMIN_USERNAME or not ADMIN_PASSWORD_HASH:
    raise RuntimeError(
        "Set JANSAARTHI_ADMIN_USERNAME and "
        "JANSAARTHI_ADMIN_PASSWORD_HASH before starting the admin app."
    )

csrf = CSRFProtect(app)
ALLOWED_STATUSES = {"Submitted", "In Progress", "Resolved"}


def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Please log in first."}), 401
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


@app.after_request
def security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "same-origin"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("dashboard"))

    error = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        username_ok = hmac.compare_digest(username, ADMIN_USERNAME)
        password_ok = check_password_hash(ADMIN_PASSWORD_HASH, password)

        if username_ok and password_ok:
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("dashboard"))

        error = "Invalid username or password."

    return render_template("admin_login.html", error=error)


@app.route("/logout", methods=["POST"])
@admin_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@admin_required
def dashboard():
    return render_template("admin.html")


@app.route("/api/admin/dashboard", methods=["GET"])
@admin_required
def dashboard_data():
    with get_connection() as connection:
        complaints = connection.execute(
            """
            SELECT complaint_id, issue, message, language, status, created_at
            FROM complaints
            ORDER BY created_at DESC
            """
        ).fetchall()

    records = [dict(row) for row in complaints]
    counts = {
        "total": len(records),
        "submitted": sum(r["status"] == "Submitted" for r in records),
        "in_progress": sum(r["status"] == "In Progress" for r in records),
        "resolved": sum(r["status"] == "Resolved" for r in records),
    }

    categories = {}
    for record in records:
        issue = record["issue"]
        categories[issue] = categories.get(issue, 0) + 1

    return jsonify({
        "demo": True,
        "counts": counts,
        "categories": categories,
        "complaints": records,
    })


@app.route("/api/admin/complaints/<complaint_id>", methods=["PATCH"])
@admin_required
def update_complaint(complaint_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ALLOWED_STATUSES:
        return jsonify({
            "error": "Choose Submitted, In Progress, or Resolved."
        }), 400

    with get_connection() as connection:
        existing = connection.execute(
            "SELECT complaint_id FROM complaints WHERE complaint_id = ?",
            (complaint_id.upper(),),
        ).fetchone()

        if existing is None:
            return jsonify({"error": "Complaint ID not found."}), 404

        connection.execute(
            "UPDATE complaints SET status = ? WHERE complaint_id = ?",
            (status, complaint_id.upper()),
        )

    return jsonify({
        "success": True,
        "complaint_id": complaint_id.upper(),
        "status": status,
        "notice": "Demo record updated locally. No government system was contacted.",
    })


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=False,
    )
