from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import current_user
from .models import db, AuditRequest

views = Blueprint("views", __name__)

@views.route("/", methods=["GET"])
def home():
    return render_template("home.html", user=current_user)

@views.route("/free-audit", methods=["POST"])
def free_audit():
    name = (request.form.get("name") or "").strip()
    email = (request.form.get("email") or "").strip()
    phone = (request.form.get("phone") or "").strip()

    brand = (request.form.get("brand") or "").strip()
    ig_handle = (request.form.get("ig_handle") or "").strip()
    website = (request.form.get("website") or "").strip()

    services = (request.form.get("services") or "").strip()
    budget = (request.form.get("budget") or "").strip()
    goals = (request.form.get("goals") or "").strip()

    if not name or not email:
        flash("Please enter your name and email.", "error")
        return redirect(url_for("views.home") + "#contact")

    lead = AuditRequest(
        name=name,
        email=email,
        phone=phone or None,
        brand=brand or None,
        ig_handle=ig_handle or None,
        website=website or None,
        services=services or None,
        budget=budget or None,
        goals=goals or None,
    )

    db.session.add(lead)
    db.session.commit()

    flash("✅ Thanks! We got your request. We'll reach out soon.", "success")
    return redirect(url_for("views.home") + "#contact")

@views.route("/test/400")
def test_400():
    abort(400)

@views.route("/test/401")
def test_401():
    abort(401)

@views.route("/test/403")
def test_403():
    abort(403)

@views.route("/test/404")
def test_404():
    abort(404)

@views.route("/test/500")
def test_500():
    1 / 0  # raises ZeroDivisionError -> 500