import os
import tempfile
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity
)
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
import io

from extractor import extract_pdf
from analyser import (analyse_text_report, analyse_scanned_report,
                      generate_summary, generate_doctor_questions, compare_reports)
from db import (save_report, save_analysis, get_all_reports, get_report_by_id,
                delete_report, create_user, get_user_by_email, get_user_by_id,
                get_reports_for_compare)
from pdf_export import generate_report_pdf

load_dotenv()

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, '..', 'frontend', 'dist')

app = Flask(__name__, static_folder=STATIC_DIR, static_url_path='')
CORS(app, supports_credentials=True)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "medeasy-secret-key")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False
jwt = JWTManager(app)

# Rate limiter — memory storage is fine for single-server deployments
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],          # no global limit — only on specific routes
    storage_uri="memory://",
)


def _err(msg, code=400):
    return jsonify({"error": msg}), code

def _ok(data, code=200):
    return jsonify(data), code

@app.errorhandler(429)
def rate_limit_handler(e):
    return _err("Too many requests. Please wait a moment and try again.", 429)


# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/api/health")
def health():
    return _ok({
        "status": "ok",
        "smtp_user": os.getenv("SMTP_USER", "NOT SET"),
        "smtp_host": os.getenv("SMTP_HOST", "NOT SET"),
        "smtp_port": os.getenv("SMTP_PORT", "NOT SET"),
        "db_host":   os.getenv("DB_HOST", "NOT SET"),
    })


# ── Auth ──────────────────────────────────────────────────────────────────────

import re as _re

def _valid_name(name: str) -> str | None:
    """Returns error string or None if valid."""
    name = name.strip()
    if len(name) < 2:
        return "Name must be at least 2 characters."
    if len(name) > 50:
        return "Name must be 50 characters or fewer."
    if not _re.match(r"^[A-Za-z\u0900-\u097F\u0A80-\u0AFF\s\-'\.]+$", name):
        return "Name can only contain letters, spaces, hyphens and dots. No numbers."
    return None

def _valid_email(email: str) -> str | None:
    if not _re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email):
        return "Please enter a valid email address."
    return None

def _valid_password(pw: str) -> str | None:
    if len(pw) < 8:
        return "Password must be at least 8 characters."
    if not _re.search(r"[0-9]", pw):
        return "Password must contain at least one number."
    if not _re.search(r"[A-Za-z]", pw):
        return "Password must contain at least one letter."
    return None


@app.route("/api/auth/register", methods=["POST"])
def register():
    data     = request.get_json() or {}
    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    err = _valid_name(name)
    if err: return _err(err)
    err = _valid_email(email)
    if err: return _err(err)
    err = _valid_password(password)
    if err: return _err(err)

    if get_user_by_email(email):
        return _err("An account with this email already exists.")

    try:
        pw_hash = generate_password_hash(password)
        user_id = create_user(name, email, pw_hash)
        token   = create_access_token(identity=str(user_id))
        return _ok({"token": token, "user": {"id": user_id, "name": name, "email": email}}, 201)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("10 per minute")       # prevent brute force
def login():
    data     = request.get_json() or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    err = _valid_email(email)
    if err: return _err(err)
    if not password:
        return _err("Password is required.")

    user = get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return _err("Invalid email or password.", 401)

    token = create_access_token(identity=str(user["id"]))
    return _ok({"token": token, "user": {"id": user["id"], "name": user["name"], "email": user["email"]}})


@app.route("/api/auth/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = get_user_by_id(user_id)
    if not user:
        return _err("User not found.", 404)
    if user.get("created_at"):
        user["created_at"] = user["created_at"].isoformat()
    return _ok(user)


# ── Analyse ───────────────────────────────────────────────────────────────────
@app.route("/api/analyse", methods=["POST"])
@jwt_required(optional=True)
def analyse():
    if "file" not in request.files:
        return _err("No file uploaded.")

    file         = request.files["file"]
    patient_name = (request.form.get("patient_name") or "").strip() or None
    lang         = request.form.get("lang", "en")
    user_id_str  = get_jwt_identity()
    user_id      = int(user_id_str) if user_id_str else None

    if not file.filename.lower().endswith(".pdf"):
        return _err("Only PDF files are supported.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name

    try:
        text, is_scanned = extract_pdf(tmp_path)
        report_id = save_report(file.filename, patient_name, text, is_scanned, user_id)

        findings  = analyse_scanned_report(tmp_path, lang) if is_scanned else analyse_text_report(text, lang)
        if not findings:
            return _err("Could not extract findings. Try a clearer PDF.", 422)

        summary   = generate_summary(findings, lang)
        questions = generate_doctor_questions(findings, lang)
        save_analysis(report_id, summary, findings, questions)

        return _ok({
            "report_id": report_id,
            "filename":  file.filename,
            "patient_name": patient_name,
            "is_scanned": is_scanned,
            "summary":   summary,
            "findings":  findings,
            "questions": questions,
            "stats": {
                "total":    len(findings),
                "normal":   sum(1 for f in findings if not f.get("flag")),
                "flagged":  sum(1 for f in findings if f.get("flag")),
                "critical": sum(1 for f in findings if f.get("status") == "Critical")
            }
        })

    except Exception as e:
        err = str(e)
        if "503" in err or "UNAVAILABLE" in err or "high demand" in err:
            return _err("AI is currently overloaded. Please wait 10–15 seconds and try again.", 503)
        if "429" in err or "RESOURCE_EXHAUSTED" in err or "rate_limit" in err.lower():
            return _err("API rate limit reached. Please wait a minute and try again.", 429)
        return _err(err, 500)
    finally:
        try: os.unlink(tmp_path)
        except: pass


# ── Reports ───────────────────────────────────────────────────────────────────
@app.route("/api/reports", methods=["GET"])
@jwt_required()
def list_reports():
    user_id = int(get_jwt_identity())
    try:
        reports = get_all_reports(user_id)
        result  = []
        for r in reports:
            row = dict(r)
            if row.get("uploaded_at"):
                row["uploaded_at"] = row["uploaded_at"].isoformat()
            result.append(row)
        return _ok(result)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/reports/<int:report_id>", methods=["GET"])
@jwt_required()
def get_report(report_id):
    user_id = int(get_jwt_identity())
    try:
        data = get_report_by_id(report_id, user_id)
        if not data:
            return _err("Report not found.", 404)
        if data["report"].get("uploaded_at"):
            data["report"]["uploaded_at"] = data["report"]["uploaded_at"].isoformat()
        return _ok(data)
    except Exception as e:
        return _err(str(e), 500)


@app.route("/api/reports/<int:report_id>", methods=["DELETE"])
@jwt_required()
def remove_report(report_id):
    user_id = int(get_jwt_identity())
    try:
        delete_report(report_id, user_id)
        return _ok({"message": "Report deleted."})
    except Exception as e:
        return _err(str(e), 500)


# ── PDF Export ────────────────────────────────────────────────────────────────
@app.route("/api/reports/<int:report_id>/export", methods=["GET"])
@jwt_required()
def export_pdf(report_id):
    user_id = int(get_jwt_identity())
    try:
        data = get_report_by_id(report_id, user_id)
        if not data:
            return _err("Report not found.", 404)
        if data["report"].get("uploaded_at"):
            data["report"]["uploaded_at"] = data["report"]["uploaded_at"].isoformat()

        pdf_bytes = generate_report_pdf(data)
        patient   = data["report"].get("patient_name") or "report"
        filename  = f"medeasy_{patient.replace(' ','_')}_{report_id}.pdf"

        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return _err(str(e), 500)


# ── Compare ───────────────────────────────────────────────────────────────────
@app.route("/api/compare", methods=["POST"])
@jwt_required()
def compare():
    user_id = int(get_jwt_identity())
    data    = request.get_json() or {}
    id_a    = data.get("report_a")
    id_b    = data.get("report_b")
    lang    = data.get("lang", "en")

    if not id_a or not id_b:
        return _err("Both report_a and report_b IDs are required.")
    if id_a == id_b:
        return _err("Please select two different reports to compare.")

    try:
        report_a, report_b = get_reports_for_compare(id_a, id_b, user_id)
        if not report_a or not report_b:
            return _err("One or both reports not found.", 404)

        findings_a = report_a["findings"]
        findings_b = report_b["findings"]

        # Normalise field names (DB uses test_name, API uses test)
        def norm(findings):
            return [{"test": f.get("test_name") or f.get("test",""),
                     "value": f.get("value",""), "status": f.get("status","")} for f in findings]

        changes = compare_reports(norm(findings_a), norm(findings_b), lang)

        if report_a["report"].get("uploaded_at"):
            report_a["report"]["uploaded_at"] = report_a["report"]["uploaded_at"].isoformat()
        if report_b["report"].get("uploaded_at"):
            report_b["report"]["uploaded_at"] = report_b["report"]["uploaded_at"].isoformat()

        return _ok({
            "report_a": {"id": id_a, "filename": report_a["report"]["filename"],
                         "date": report_a["report"].get("uploaded_at")},
            "report_b": {"id": id_b, "filename": report_b["report"]["filename"],
                         "date": report_b["report"].get("uploaded_at")},
            "changes": changes
        })
    except Exception as e:
        return _err(str(e), 500)



# ── Serve React in production ─────────────────────────────────────────────────
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_react(path):
    """Serve the React build. All non-API routes return index.html."""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(debug=debug, host="0.0.0.0", port=port)
