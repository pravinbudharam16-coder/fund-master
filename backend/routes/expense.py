from flask import Blueprint, render_template, request, redirect, session
from backend.database import db
from backend.models import Expense

expense_bp = Blueprint("expense", __name__)

@expense_bp.route("/expense", methods=["GET", "POST"])
def expense():
    print("ROUTE HIT")   # 🔴 MUST PRINT EVERY TIME

    if request.method == "POST":
        print("POST METHOD")          # 🔴 MUST PRINT
        print(request.form)           # 🔴 MUST PRINT DATA

        if "user_id" not in session:
            print("NO USER IN SESSION")
            return redirect("/login")

        exp = Expense(
            title=request.form.get("title"),
            amount=float(request.form.get("amount")),
            category=request.form.get("category"),
            date=request.form.get("date"),
            user_id=session["user_id"]
        )

        db.session.add(exp)
        db.session.commit()

        print("COMMITTED TO DB")       # 🔴 MUST PRINT
        return redirect("/expense")

    if "user_id" not in session:
      return redirect("/login")

    report = Expense.query.filter_by(user_id=session["user_id"]).all()
    return render_template("expense.html", report=report)

@expense_bp.route("/expense/delete/<int:id>")
def delete_expense(id):
    if "user_id" not in session:
        return redirect("/login")

    expense = Expense.query.filter_by(
        id=id,
        user_id=session["user_id"]
    ).first()

    if expense:
        db.session.delete(expense)
        db.session.commit()

    return redirect("/expense")