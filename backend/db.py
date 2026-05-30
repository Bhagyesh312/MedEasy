import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    sslmode = os.getenv("DB_SSLMODE", None)
    kwargs = dict(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432),
        dbname=os.getenv("DB_NAME", "medical_report_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", "")
    )
    if sslmode:
        kwargs["sslmode"] = sslmode
    return psycopg2.connect(**kwargs)


# ── Auth ──────────────────────────────────────────────────────────────────────

def create_user(name, email, password_hash):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                (name, email, password_hash)
            )
            user_id = cur.fetchone()[0]
        conn.commit()
        return user_id
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE email = %s", (email,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT id, name, email, created_at FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()


# ── Reports ───────────────────────────────────────────────────────────────────

def save_report(filename, patient_name, raw_text, is_scanned, user_id=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO reports (filename, patient_name, raw_text, is_scanned, status, user_id)
                   VALUES (%s, %s, %s, %s, 'pending', %s) RETURNING id""",
                (filename, patient_name, raw_text, is_scanned, user_id)
            )
            report_id = cur.fetchone()[0]
        conn.commit()
        return report_id
    finally:
        conn.close()


def save_analysis(report_id, summary, findings, questions):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE reports SET summary = %s, status = 'analysed' WHERE id = %s",
                (summary, report_id)
            )
            for f in findings:
                cur.execute(
                    """INSERT INTO findings
                       (report_id, test_name, value, reference_range, status, explanation, action, is_flagged)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (report_id, f.get("test","Unknown"), f.get("value","N/A"),
                     f.get("reference_range","Not specified"), f.get("status","Unknown"),
                     f.get("explanation",""), f.get("action",""), bool(f.get("flag",False)))
                )
            for q in questions:
                cur.execute(
                    "INSERT INTO doctor_questions (report_id, question) VALUES (%s, %s)",
                    (report_id, q)
                )
        conn.commit()
    finally:
        conn.close()


def get_all_reports(user_id=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if user_id:
                cur.execute(
                    """SELECT id, filename, patient_name, uploaded_at, status,
                              (SELECT COUNT(*) FROM findings WHERE report_id=reports.id AND is_flagged=TRUE) AS flagged_count,
                              (SELECT COUNT(*) FROM findings WHERE report_id=reports.id) AS total_tests
                       FROM reports WHERE user_id=%s ORDER BY uploaded_at DESC""",
                    (user_id,)
                )
            else:
                cur.execute(
                    """SELECT id, filename, patient_name, uploaded_at, status,
                              (SELECT COUNT(*) FROM findings WHERE report_id=reports.id AND is_flagged=TRUE) AS flagged_count,
                              (SELECT COUNT(*) FROM findings WHERE report_id=reports.id) AS total_tests
                       FROM reports ORDER BY uploaded_at DESC"""
                )
            return cur.fetchall()
    finally:
        conn.close()


def get_report_by_id(report_id, user_id=None):
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if user_id:
                cur.execute("SELECT * FROM reports WHERE id=%s AND user_id=%s", (report_id, user_id))
            else:
                cur.execute("SELECT * FROM reports WHERE id=%s", (report_id,))
            report = cur.fetchone()
            if not report:
                return None
            cur.execute(
                "SELECT * FROM findings WHERE report_id=%s ORDER BY is_flagged DESC, id ASC",
                (report_id,)
            )
            findings = cur.fetchall()
            cur.execute("SELECT question FROM doctor_questions WHERE report_id=%s", (report_id,))
            questions = [r["question"] for r in cur.fetchall()]
            return {
                "report": dict(report),
                "findings": [dict(f) for f in findings],
                "questions": questions
            }
    finally:
        conn.close()


def delete_report(report_id, user_id=None):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if user_id:
                cur.execute("DELETE FROM reports WHERE id=%s AND user_id=%s", (report_id, user_id))
            else:
                cur.execute("DELETE FROM reports WHERE id=%s", (report_id,))
        conn.commit()
    finally:
        conn.close()


def get_reports_for_compare(report_id_a, report_id_b, user_id=None):
    """Fetch two reports' findings for comparison."""
    a = get_report_by_id(report_id_a, user_id)
    b = get_report_by_id(report_id_b, user_id)
    return a, b


# ── OTP ───────────────────────────────────────────────────────────────────────

def save_otp(email: str, code: str, purpose: str = "register"):
    """Store a new OTP, invalidating any previous ones for this email+purpose."""
    from datetime import datetime, timedelta
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Invalidate old codes for this email+purpose
            cur.execute(
                "UPDATE otp_codes SET used=TRUE WHERE email=%s AND purpose=%s AND used=FALSE",
                (email, purpose)
            )
            expires_at = datetime.utcnow() + timedelta(minutes=10)
            cur.execute(
                "INSERT INTO otp_codes (email, code, purpose, expires_at) VALUES (%s,%s,%s,%s)",
                (email, code, purpose, expires_at)
            )
        conn.commit()
    finally:
        conn.close()


def verify_otp(email: str, code: str, purpose: str = "register") -> bool:
    """Check OTP is valid, not expired, not used. Marks it used on success."""
    from datetime import datetime
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT id FROM otp_codes
                   WHERE email=%s AND code=%s AND purpose=%s
                     AND used=FALSE AND expires_at > %s
                   ORDER BY created_at DESC LIMIT 1""",
                (email, code, purpose, datetime.utcnow())
            )
            row = cur.fetchone()
            if not row:
                return False
            cur.execute("UPDATE otp_codes SET used=TRUE WHERE id=%s", (row[0],))
        conn.commit()
        return True
    finally:
        conn.close()


def cleanup_expired_otps():
    """Delete OTPs older than 1 hour (call periodically)."""
    from datetime import datetime, timedelta
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cutoff = datetime.utcnow() - timedelta(hours=1)
            cur.execute("DELETE FROM otp_codes WHERE created_at < %s", (cutoff,))
        conn.commit()
    finally:
        conn.close()
