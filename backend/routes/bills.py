from flask import Blueprint, render_template, request, redirect, session
from backend.database import db
from backend.models import Bill
from datetime import datetime, date

bills_bp = Blueprint("bills", __name__)


@bills_bp.route("/bills", methods=["GET", "POST"])
def bills():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":
        db.session.add(Bill(
            user_id=user_id,
            title=request.form.get("title"),
            amount=float(request.form.get("amount")),
            due_date=request.form.get("due_date"),
            category=request.form.get("category", "Bill")
        ))
        db.session.commit()
        return redirect("/bills")

    today = date.today().isoformat()
    all_bills = Bill.query.filter_by(user_id=user_id).order_by(Bill.due_date).all()

    overdue  = [b for b in all_bills if b.due_date < today and not b.is_paid]
    upcoming = [b for b in all_bills if b.due_date >= today and not b.is_paid]
    paid     = [b for b in all_bills if b.is_paid]

    return render_template("bills.html",
        overdue=overdue,
        upcoming=upcoming,
        paid=paid,
        today=today
    )


@bills_bp.route("/bills/paid/<int:id>")
def mark_paid(id):
    if "user_id" not in session:
        return redirect("/login")
    b = Bill.query.filter_by(id=id, user_id=session["user_id"]).first_or_404()
    b.is_paid = True
    db.session.commit()
    return redirect("/bills")


@bills_bp.route("/bills/delete/<int:id>")
def delete_bill(id):
    if "user_id" not in session:
        return redirect("/login")
    b = Bill.query.filter_by(id=id, user_id=session["user_id"]).first_or_404()
    db.session.delete(b)
    db.session.commit()
    return redirect("/bills")
