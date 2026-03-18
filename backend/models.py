from backend.database import db
from werkzeug.security import generate_password_hash

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

class Income(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    source = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.String(20), nullable=False)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    amount = db.Column(db.Float)
    category = db.Column(db.String(50))
    date = db.Column(db.String(20))
    user_id = db.Column(db.Integer)

class Asset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, nullable=False)

# ── NEW MODELS ───────────────────────────────────────────────

class Budget(db.Model):
    """Monthly budget limit per expense category."""
    __tablename__ = "budgets"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    limit_amount = db.Column(db.Float, nullable=False)
    month = db.Column(db.String(7), nullable=False)   # format: YYYY-MM


class Bill(db.Model):
    """Bill / EMI reminder tracker."""
    __tablename__ = "bills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.String(20), nullable=False)   # format: YYYY-MM-DD
    category = db.Column(db.String(50), default="Bill")   # Bill / EMI / Subscription
    is_paid = db.Column(db.Boolean, default=False)


class SavingsGoal(db.Model):
    """Monthly savings goal tracker."""
    __tablename__ = "savings_goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    saved_amount = db.Column(db.Float, default=0.0)
    deadline = db.Column(db.String(20), nullable=True)    # format: YYYY-MM-DD
