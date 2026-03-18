from flask import Blueprint, render_template, request, redirect, session
from backend.database import db
from backend.models import Income

income_bp = Blueprint("income", __name__)

@income_bp.route("/income", methods=["GET", "POST"])
def income():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        inc = Income(
            source=request.form["source"],
            amount=float(request.form["amount"]),
            date=request.form["date"],
            user_id=session["user_id"]
        )
        db.session.add(inc)
        db.session.commit()
        return redirect("/income")

    report = Income.query.filter_by(user_id=session["user_id"]).all()
    return render_template("income.html", report=report)


@income_bp.route("/income/delete/<int:id>")
def delete_income(id):
    if "user_id" not in session:
        return redirect("/login")

    inc = Income.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()

    if inc:
        db.session.delete(inc)
        db.session.commit()

    return redirect("/income")