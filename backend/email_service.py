import smtplib
import random
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST     = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT     = int(os.getenv("SMTP_PORT", 587))
SMTP_USER     = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM     = os.getenv("SMTP_FROM", SMTP_USER)

OTP_EXPIRY_MINUTES = 10


def generate_otp() -> str:
    """Generate a 6-digit numeric OTP."""
    return ''.join(random.choices(string.digits, k=6))


def send_otp_email(to_email: str, otp: str, name: str = "") -> bool:
    """Send OTP email via Gmail SMTP. Returns True on success."""
    greeting = f"Hi {name}," if name else "Hi,"

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f5f5f4;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f5f5f4;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;border:1px solid #e7e5e4;overflow:hidden;">

          <!-- Header -->
          <tr>
            <td style="background:#0f766e;padding:24px 32px;">
              <p style="margin:0;color:#ffffff;font-size:18px;font-weight:700;letter-spacing:-0.3px;">MedEasy</p>
              <p style="margin:4px 0 0;color:rgba(255,255,255,0.75);font-size:12px;">Medical Report Simplifier</p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="padding:32px;">
              <p style="margin:0 0 8px;color:#1c1917;font-size:15px;">{greeting}</p>
              <p style="margin:0 0 24px;color:#44403c;font-size:14px;line-height:1.6;">
                Use the verification code below to complete your sign up. This code expires in <strong>{OTP_EXPIRY_MINUTES} minutes</strong>.
              </p>

              <!-- OTP Box -->
              <div style="background:#f5f5f4;border:1px solid #e7e5e4;border-radius:8px;padding:24px;text-align:center;margin-bottom:24px;">
                <p style="margin:0 0 6px;color:#78716c;font-size:11px;font-weight:600;text-transform:uppercase;letter-spacing:1px;">Verification Code</p>
                <p style="margin:0;color:#0f766e;font-size:36px;font-weight:700;letter-spacing:10px;font-family:'Courier New',monospace;">{otp}</p>
              </div>

              <p style="margin:0 0 8px;color:#78716c;font-size:13px;line-height:1.6;">
                If you didn't request this code, you can safely ignore this email.
              </p>
              <p style="margin:0;color:#78716c;font-size:13px;">
                Never share this code with anyone.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:16px 32px;border-top:1px solid #e7e5e4;">
              <p style="margin:0;color:#a8a29e;font-size:11px;">
                MedEasy &mdash; This is an automated message, please do not reply.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

    plain_body = f"""{greeting}

Your MedEasy verification code is: {otp}

This code expires in {OTP_EXPIRY_MINUTES} minutes.
If you didn't request this, ignore this email.

— MedEasy Team
"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"{otp} is your MedEasy verification code"
    msg["From"]    = SMTP_FROM
    msg["To"]      = to_email

    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body,  "html"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[email_service] Failed to send OTP to {to_email}: {e}")
        return False
