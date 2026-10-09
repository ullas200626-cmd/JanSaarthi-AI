
from flask import Flask, render_template, jsonify, request
from database import get_connection

app = Flask(__name__)

ALLOWED_STATUSES = {"Submitted", "In Progress", "Resolved"}


@app.route("/")
def dashboard():
    return render_template("admin.html")


@app.route("/api/admin/dashboard", methods=["GET"])
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
            return jsonify({
                "error": "Complaint ID not found."
            }), 404

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
    print("JanSaarthi AI Demo Admin Dashboard")
    print("Open http://127.0.0.1:5001")
    print("Prototype only: this dashboard has no administrator login.")
    app.run(port=5001, debug=True)