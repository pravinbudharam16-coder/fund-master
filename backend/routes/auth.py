from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_

from backend.database import db
from backend.models import User
from backend.email_utils import send_otp

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identity = request.form.get("identity")
        password = request.form.get("password")

        user = User.query.filter(
            or_(User.email == identity, User.username == identity)
        ).first()

        if not user or not check_password_hash(user.password, password):
            return render_template("login.html", error="Incorrect username or password")

        session["user_id"] = user.id
        return redirect("/dashboard")

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email    = request.form.get("email")
        password = request.form.get("password")

        if User.query.filter(
            or_(User.username == username, User.email == email)
        ).first():
            return render_template("register.html", error="User already exists")

        user = User(
            username=username,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/login")

    return render_template("register.html")


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    session.pop("reset_otp",    None)
    session.pop("reset_email",  None)
    session.pop("otp_verified", None)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        print("=== FORGOT PASSWORD ===")
        print("Email entered:", email)
        
        user = User.query.filter_by(email=email).first()
        print("User found:", user)
        
        if not user:
            print("ERROR: Email not registered")
            return render_template("forgot_password.html",
                error="Email not registered")

        otp = send_otp(email)
        session["reset_otp"]   = str(otp)
        session["reset_email"] = email
        print("OTP generated:", otp)
        print("Session after setting:", dict(session))
        
        return render_template("verify_otp.html",
            message="OTP sent to your email!")

    return render_template("forgot_password.html")


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    # Must have a pending OTP in session
    if not session.get("reset_otp"):
        return redirect("/forgot-password")

    if request.method == "POST":
        entered = request.form.get("otp", "").strip()
        stored  = str(session.get("reset_otp", ""))

        print(f"Entered OTP: {entered} | Stored OTP: {stored}")

        if entered != stored:
            return render_template("verify_otp.html",
                error="Invalid OTP. Please try again.")

        session["otp_verified"] = True
        return redirect("/reset-password")

    return render_template("verify_otp.html")


@auth_bp.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    # Must have verified OTP first
    if not session.get("otp_verified"):
        return redirect("/forgot-password")

    if request.method == "POST":
        new_pw     = request.form.get("new_password", "")
        confirm_pw = request.form.get("confirm_password", "")

        if len(new_pw) < 6:
            return render_template("reset_password.html",
                error="Password must be at least 6 characters.")

        if new_pw != confirm_pw:
            return render_template("reset_password.html",
                error="Passwords do not match.")

        email = session.get("reset_email")
        user  = User.query.filter_by(email=email).first()

        if user:
            user.password = generate_password_hash(new_pw)
            db.session.commit()

        # Clear all reset session data
        session.pop("reset_otp",    None)
        session.pop("reset_email",  None)
        session.pop("otp_verified", None)

        return redirect("/login")

    return render_template("reset_password.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")
