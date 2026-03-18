from flask import Blueprint, render_template, request, redirect, session
from backend.database import db
from backend.models import Budget, Expense
from sqlalchemy import func
from datetime import datetime

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/budget", methods=["GET", "POST"])
def budget():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    current_month = datetime.now().strftime("%Y-%m")

    if request.method == "POST":
        category     = request.form.get("category", "").strip()
        limit_str    = request.form.get("limit_amount", "").strip()
        month        = request.form.get("month", "").strip() or current_month

        print("BUDGET POST — category:", category, "limit:", limit_str, "month:", month)

        if category and limit_str:
            existing = Budget.query.filter_by(
                user_id=user_id, category=category, month=month
            ).first()

            if existing:
                existing.limit_amount = float(limit_str)
                print("UPDATED existing budget")
            else:
                db.session.add(Budget(
                    user_id=user_id,
                    category=category,
                    limit_amount=float(limit_str),
                    month=month
                ))
                print("ADDED new budget")

            db.session.commit()

        return redirect("/budget")

    # Fetch budgets for current month
    budgets = Budget.query.filter_by(user_id=user_id, month=current_month).all()

    budget_data = []
    for b in budgets:
        spent = db.session.query(func.sum(Expense.amount)).filter(
            Expense.user_id == user_id,
            Expense.category == b.category,
            Expense.date.like(f"{current_month}%")
        ).scalar() or 0

        percent = round((spent / b.limit_amount) * 100) if b.limit_amount > 0 else 0
        percent = min(percent, 100)

        status = "danger" if percent >= 100 else "warning" if percent >= 75 else "safe"

        budget_data.append({
            "id": b.id,
            "category": b.category,
            "limit": b.limit_amount,
            "spent": spent,
            "remaining": max(b.limit_amount - spent, 0),
            "percent": percent,
            "status": status
        })

    return render_template("budget.html",
        budget_data=budget_data,
        current_month=current_month
    )


@budget_bp.route("/budget/delete/<int:id>")
def delete_budget(id):
    if "user_id" not in session:
        return redirect("/login")
    b = Budget.query.filter_by(id=id, user_id=session["user_id"]).first_or_404()
    db.session.delete(b)
    db.session.commit()
    return redirect("/budget")
