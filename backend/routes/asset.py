from flask import Blueprint, render_template, request, redirect, session
from backend.database import db
from backend.models import Asset

asset_bp = Blueprint("asset", __name__)

@asset_bp.route("/asset", methods=["GET", "POST"])
def asset():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    if request.method == "POST":
        name = request.form["name"]
        value = request.form["value"]

        new_asset = Asset(
            name=name,
            value=value,
            user_id=user_id
        )

        db.session.add(new_asset)
        db.session.commit()

        return redirect("/asset")

    assets = Asset.query.filter_by(user_id=user_id).all()
    return render_template("asset.html", assets=assets)


@asset_bp.route("/asset/delete/<int:id>")
def delete_asset(id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")

    asset = Asset.query.filter_by(id=id, user_id=user_id).first_or_404()
    db.session.delete(asset)
    db.session.commit()
    return redirect("/asset")