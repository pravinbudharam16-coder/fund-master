from flask import Blueprint, render_template, session, redirect
from backend.database import db
from backend.models import Income, Expense, Asset
from sqlalchemy import func

analysis_bp = Blueprint("analysis", __name__)

@analysis_bp.route("/analysis")
def analysis():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    # Totals
    total_income = db.session.query(
        func.sum(Income.amount)
    ).filter(Income.user_id == user_id).scalar() or 0

    total_expense = db.session.query(
        func.sum(Expense.amount)
    ).filter(Expense.user_id == user_id).scalar() or 0

    total_balance = total_income - total_expense

    total_assets = db.session.query(
        func.sum(Asset.value)
    ).filter(Asset.user_id == user_id).scalar() or 0

    # Savings rate
    savings_rate = round((total_balance / total_income * 100), 1) if total_income > 0 else 0

    # Expense by category
    category_data = db.session.query(
        Expense.category, func.sum(Expense.amount)
    ).filter(Expense.user_id == user_id).group_by(Expense.category).all()

    category_labels = [row[0] or "Other" for row in category_data]
    category_values = [row[1] for row in category_data]

    # Income by source
    source_data = db.session.query(
        Income.source, func.sum(Income.amount)
    ).filter(Income.user_id == user_id).group_by(Income.source).all()

    source_labels = [row[0] for row in source_data]
    source_values = [row[1] for row in source_data]

    # Monthly expense trend (last 6 months)
    monthly_data = db.session.query(
        func.substr(Expense.date, 1, 7).label("month"),
        func.sum(Expense.amount)
    ).filter(Expense.user_id == user_id).group_by("month").order_by("month").limit(6).all()

    monthly_labels = [row[0] for row in monthly_data]
    monthly_values = [row[1] for row in monthly_data]

    return render_template("analysis.html",
        total_income=total_income,
        total_expense=total_expense,
        total_balance=total_balance,
        total_assets=total_assets,
        savings_rate=savings_rate,
        category_labels=category_labels,
        category_values=category_values,
        source_labels=source_labels,
        source_values=source_values,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values
    )
