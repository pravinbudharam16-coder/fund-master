from flask import Blueprint, request, jsonify, session
from groq import Groq
import os
from dotenv import load_dotenv
from backend.database import db
from backend.models import Income, Expense, Asset
from sqlalchemy import func

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

ai_chat_bp = Blueprint("ai_chat", __name__)


def get_user_financial_data(user_id):
    total_income = db.session.query(
        func.sum(Income.amount)
    ).filter(Income.user_id == user_id).scalar() or 0

    total_expense = db.session.query(
        func.sum(Expense.amount)
    ).filter(Expense.user_id == user_id).scalar() or 0

    total_balance = total_income - total_expense

    income_records = Income.query.filter_by(user_id=user_id).order_by(Income.id.desc()).limit(5).all()
    income_sources = [{"source": i.source, "amount": i.amount, "date": i.date} for i in income_records]

    expense_records = Expense.query.filter_by(user_id=user_id).all()
    category_totals = {}
    for e in expense_records:
        cat = e.category or "Other"
        category_totals[cat] = category_totals.get(cat, 0) + e.amount

    asset_records = Asset.query.filter_by(user_id=user_id).all()
    assets = [{"name": a.name, "value": a.value} for a in asset_records]
    total_assets = sum(a.value for a in asset_records)

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_balance": total_balance,
        "total_assets": total_assets,
        "income_sources": income_sources,
        "category_totals": category_totals,
        "assets": assets
    }


def build_system_prompt(user_data):
    category_str = ", ".join([f"{k}: Rs.{v:,.0f}" for k, v in user_data["category_totals"].items()]) or "No expense data"
    assets_str   = ", ".join([f"{a['name']}: Rs.{a['value']:,.0f}" for a in user_data["assets"]]) or "No assets"
    income_str   = ", ".join([f"{i['source']} Rs.{i['amount']:,.0f} on {i['date']}" for i in user_data["income_sources"]]) or "No income records"

    return f"""You are a personal AI financial assistant inside Fund Master, a personal finance app.
You ONLY answer questions related to this specific user's financial data shown below.
If asked anything unrelated to their finances, say:
"I can only help with questions about your Fund Master account and financial data."

--- USER FINANCIAL DATA ---
Total Income:  Rs.{user_data['total_income']:,.2f}
Total Expense: Rs.{user_data['total_expense']:,.2f}
Total Balance: Rs.{user_data['total_balance']:,.2f}
Total Assets:  Rs.{user_data['total_assets']:,.2f}

Recent Income: {income_str}
Expenses by Category: {category_str}
Assets: {assets_str}

--- INSTRUCTIONS ---
- Always use Rs. for currency amounts
- Be concise, friendly, and specific to their actual numbers
- If data is zero or empty, mention they have not added records yet
- Never make up data that is not in the above section
"""


@ai_chat_bp.route("/api/ai-chat", methods=["POST"])
def chat():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    user_data = get_user_financial_data(user_id)
    system_prompt = build_system_prompt(user_data)

    # Build messages with system prompt
    groq_messages = [{"role": "system", "content": system_prompt}]
    for msg in messages:
        groq_messages.append({"role": msg["role"], "content": msg["content"]})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # free model on Groq
            messages=groq_messages,
            max_tokens=1024
        )
        reply = response.choices[0].message.content
        return jsonify({"reply": reply})

    except Exception as e:
        print("AI CHAT ERROR:", str(e))
        return jsonify({"error": str(e)}), 500
