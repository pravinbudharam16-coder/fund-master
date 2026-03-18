from flask import Blueprint, render_template, jsonify

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/prediction")
def prediction_page():
    return render_template("prediction.html")

@prediction_bp.route("/api/prediction")
def prediction_api():
    income = 50000
    expense = 32000
    savings = income - expense

    return jsonify({
        "predicted_income": income,
        "predicted_expense": expense,
        "predicted_savings": savings
    })