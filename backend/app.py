from flask import Flask, redirect
from backend.database import db

def create_app():
    app = Flask(__name__)
    app.secret_key = "fund-master-super-secret-key-2026-xyz"

    app.config["SESSION_COOKIE_SECURE"] = False
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///fundmaster.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from backend.routes.auth import auth_bp
    from backend.routes.dashboard import dashboard_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)

    from backend.routes.income import income_bp
    app.register_blueprint(income_bp)

    from backend.routes.expense import expense_bp
    app.register_blueprint(expense_bp)

    from backend.routes.asset import asset_bp
    app.register_blueprint(asset_bp)

    from backend.routes.analysis import analysis_bp
    app.register_blueprint(analysis_bp)

    from backend.routes.settings import settings_bp
    app.register_blueprint(settings_bp)

    from backend.routes.ai_chat import ai_chat_bp
    app.register_blueprint(ai_chat_bp)

    from backend.routes.report import report_bp
    app.register_blueprint(report_bp)

    from backend.routes.budget import budget_bp
    app.register_blueprint(budget_bp)

    from backend.routes.bills import bills_bp
    app.register_blueprint(bills_bp)

    from backend.routes.savings import savings_bp
    app.register_blueprint(savings_bp)

    @app.route("/")
    def home():
        return redirect("/login")

    @app.route("/__routes__")
    def show_routes():
        return "<br>".join(str(r) for r in app.url_map.iter_rules())

    return app
