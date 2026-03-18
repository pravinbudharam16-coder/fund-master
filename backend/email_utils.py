import smtplib
import random
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

MAIL_EMAIL    = os.getenv("MAIL_EMAIL")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")


def send_otp(email):
    otp = str(random.randint(100000, 999999))

    # ── Build Email ──────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Fund Master — Your OTP Code"
    msg["From"]    = MAIL_EMAIL
    msg["To"]      = email

    # Plain text version
    text = f"""
Hello,

Your OTP for Fund Master password reset is:

{otp}

This OTP is valid for 10 minutes.
Do not share this code with anyone.

— Fund Master Team
"""

    # HTML version
    html = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',sans-serif;">
  <div style="max-width:480px;margin:40px auto;background:#0b1f24;border-radius:16px;
    border:1px solid rgba(0,242,255,0.2);overflow:hidden;">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#00f2ff,#00c6ff);padding:24px;text-align:center;">
      <h1 style="margin:0;color:#002b36;font-size:22px;font-weight:700;">Fund Master</h1>
      <p style="margin:4px 0 0;color:#003844;font-size:13px;">Your Personal Finance Assistant</p>
    </div>

    <!-- Body -->
    <div style="padding:32px 28px;">
      <p style="color:#b0bec5;font-size:15px;margin:0 0 10px;">Hello,</p>
      <p style="color:#b0bec5;font-size:15px;margin:0 0 24px;">
        We received a request to reset your Fund Master password.
        Use the OTP below to proceed:
      </p>

      <!-- OTP Box -->
      <div style="background:rgba(0,242,255,0.08);border:1px solid rgba(0,242,255,0.3);
        border-radius:12px;padding:20px;text-align:center;margin-bottom:24px;">
        <p style="margin:0 0 6px;color:rgba(0,242,255,0.7);font-size:13px;letter-spacing:1px;">
          YOUR OTP CODE
        </p>
        <p style="margin:0;color:#00f2ff;font-size:38px;font-weight:700;
          letter-spacing:12px;text-shadow:0 0 20px rgba(0,242,255,0.5);">
          {otp}
        </p>
      </div>

      <p style="color:#b0bec5;font-size:13px;margin:0 0 8px;">
        ⏱ This OTP is valid for <strong style="color:#e2e8f0;">10 minutes</strong>.
      </p>
      <p style="color:#b0bec5;font-size:13px;margin:0;">
        🔒 Do not share this code with anyone.
      </p>
    </div>

    <!-- Footer -->
    <div style="padding:16px 28px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
      <p style="color:rgba(176,190,197,0.4);font-size:12px;margin:0;">
        If you didn't request this, please ignore this email.<br>
        — Fund Master Team
      </p>
    </div>

  </div>
</body>
</html>
"""

    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html,  "html"))

    # ── Send via Gmail SMTP ──────────────────────────────────
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(MAIL_EMAIL, MAIL_PASSWORD)
            server.sendmail(MAIL_EMAIL, email, msg.as_string())
            print(f"OTP email sent to {email}")
        return otp

    except Exception as e:
        print(f"Email error: {e}")
        # Fallback — print to terminal so app doesn't break
        print("====== FALLBACK OTP (email failed) ======")
        print(f"Email: {email}  OTP: {otp}")
        print("=========================================")
        return otp
