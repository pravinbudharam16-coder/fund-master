from flask import Blueprint, render_template, request, redirect, session
from backend.database import db
from backend.models import SavingsGoal

savings_bp = Blueprint("savings", __name__)


@savings_bp.route("/savings", methods=["GET", "POST"])
def savings():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":
        title      = request.form.get("title", "").strip()
        target_str = request.form.get("target_amount", "").strip()
        deadline   = request.form.get("deadline") or None

        if title and target_str:
            db.session.add(SavingsGoal(
                user_id=user_id,
                title=title,
                target_amount=float(target_str),
                saved_amount=0.0,
                deadline=deadline
            ))
            db.session.commit()

        return redirect("/savings")

    goals = SavingsGoal.query.filter_by(user_id=user_id).all()
    goals_data = []
    for g in goals:
        percent   = round((g.saved_amount / g.target_amount) * 100) if g.target_amount > 0 else 0
        percent   = min(percent, 100)
        remaining = max(g.target_amount - g.saved_amount, 0)
        status    = "complete" if percent >= 100 else "progress" if percent >= 50 else "start"
        goals_data.append({
            "id": g.id, "title": g.title,
            "target": g.target_amount, "saved": g.saved_amount,
            "remaining": remaining, "percent": percent,
            "deadline": g.deadline, "status": status
        })

    return render_template("savings.html", goals_data=goals_data)


@savings_bp.route("/savings/add/<int:goal_id>", methods=["POST"])
def add_savings(goal_id):
    if "user_id" not in session:
        return redirect("/login")

    amount_str = request.form.get("amount", "").strip()
    print("ADD SAVINGS — goal_id:", goal_id, "amount:", amount_str)

    if amount_str:
        goal = SavingsGoal.query.filter_by(
            id=goal_id, user_id=session["user_id"]
        ).first()
        if goal:
            goal.saved_amount = min(
                goal.saved_amount + float(amount_str),
                goal.target_amount
            )
            db.session.commit()
            print("SAVED:", goal.saved_amount)

    return redirect("/savings")


@savings_bp.route("/savings/delete/<int:id>")
def delete_goal(id):
    if "user_id" not in session:
        return redirect("/login")
    g = SavingsGoal.query.filter_by(id=id, user_id=session["user_id"]).first_or_404()
    db.session.delete(g)
    db.session.commit()
    return redirect("/savings")
