from flask import Blueprint, render_template, session, redirect, request, flash
from backend.database import db
from backend.models import User
from werkzeug.security import check_password_hash, generate_password_hash

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings", methods=["GET", "POST"])
def settings():
    if "user_id" not in session:
        return redirect("/login")

    user = User.query.get(session["user_id"])
    message = None
    error = None

    if request.method == "POST":
        action = request.form.get("action")

        # --- Update Profile ---
        if action == "update_profile":
            new_username = request.form.get("username", "").strip()
            new_email    = request.form.get("email", "").strip()

            if not new_username or not new_email:
                error = "Username and email cannot be empty."
            else:
                # Check if username/email taken by another user
                existing = User.query.filter(
                    (User.username == new_username) | (User.email == new_email)
                ).first()

                if existing and existing.id != user.id:
                    error = "Username or email already taken by another account."
                else:
                    user.username = new_username
                    user.email    = new_email
                    db.session.commit()
                    message = "Profile updated successfully."

        # --- Change Password ---
        elif action == "change_password":
            current_pw  = request.form.get("current_password", "")
            new_pw      = request.form.get("new_password", "")
            confirm_pw  = request.form.get("confirm_password", "")

            if not check_password_hash(user.password, current_pw):
                error = "Current password is incorrect."
            elif len(new_pw) < 6:
                error = "New password must be at least 6 characters."
            elif new_pw != confirm_pw:
                error = "New passwords do not match."
            else:
                user.password = generate_password_hash(new_pw)
                db.session.commit()
                message = "Password changed successfully."

    return render_template("settings.html", user=user, message=message, error=error)
