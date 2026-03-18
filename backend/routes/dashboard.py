from flask import Blueprint, render_template, session, redirect
from backend.database import db
from backend.models import Income
from backend.models import Expense
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    total_income = db.session.query(
        func.sum(Income.amount)
    ).filter(
        Income.user_id == session["user_id"]
    ).scalar() or 0

    total_expense = db.session.query(
        func.sum(Expense.amount)
    ).filter(
        Expense.user_id == session["user_id"]
    ).scalar() or 0

    total_balance = total_income - total_expense

    print("BALANCE UPDATED:", total_income, total_expense, total_balance)

    return render_template(
        "dashboard.html",
        total_income=total_income,
        total_expense=total_expense,
        total_balance=total_balance
    )