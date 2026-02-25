from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from .models import db, AdminUser, AuditRequest

auth = Blueprint("auth", __name__)

def any_admin_exists() -> bool:
    return db.session.query(AdminUser.id).first() is not None

# ---------------------------
# Admin Login
# URL: /admin/login
# Template: admin_login.html
# ---------------------------
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        user = AdminUser.query.filter_by(email=email).first()
        if not user or not user.check_password(password) or not user.is_active:
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("auth.audits"))

    return render_template("admin_login.html")


# ---------------------------
# Admin Signup (Add Admins)
# URL: /admin/signup
# Template: admin_signup.html
#
# Rules:
# - If at least one admin exists: require login
# - If no admins exist yet: allow first admin creation without login
# ---------------------------
@auth.route("/signup", methods=["GET", "POST"])
def signup():
    admins_exist = any_admin_exists()

    # If admins already exist, only logged-in admins can create more.
    if admins_exist and not current_user.is_authenticated:
        flash("Please login to add admins.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        confirm = request.form.get("confirm_password") or ""

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("auth.signup"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.signup"))

        if len(password) < 8:
            flash("Password must be at least 8 characters.", "error")
            return redirect(url_for("auth.signup"))

        if AdminUser.query.filter_by(email=email).first():
            flash("That admin email already exists.", "error")
            return redirect(url_for("auth.signup"))

        new_admin = AdminUser(email=email)
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()

        # If this is the first admin, log them in automatically
        if not admins_exist:
            login_user(new_admin)
            flash("✅ First admin created. You're now logged in.", "success")
            return redirect(url_for("auth.audits"))

        flash("✅ Admin added successfully.", "success")
        return redirect(url_for("auth.audits"))

    return render_template("admin_signup.html", admins_exist=admins_exist)


# ---------------------------
# Logout
# URL: /admin/logout
# ---------------------------
@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# ---------------------------
# Admin Audits List
# URL: /admin/audits
# Template: admin_audits.html
# ---------------------------
@auth.route("/audits", methods=["GET"])
@login_required
def audits():
    status = request.args.get("status")
    q = AuditRequest.query
    if status:
        q = q.filter_by(status=status)

    audits = q.order_by(AuditRequest.created_at.desc()).all()
    return render_template("admin_audits.html", audits=audits, active_status=status)


# ---------------------------
# Admin Audit Detail
# URL: /admin/audits/<id>
# Template: admin_audit_detail.html
# ---------------------------
@auth.route("/audits/<int:audit_id>", methods=["GET", "POST"])
@login_required
def audit_detail(audit_id):
    audit = AuditRequest.query.get_or_404(audit_id)

    if request.method == "POST":
        audit.status = (request.form.get("status") or audit.status or "New").strip()
        audit.admin_notes = (request.form.get("admin_notes") or "").strip() or None
        db.session.commit()

        flash("Saved ✅", "success")
        return redirect(url_for("auth.audit_detail", audit_id=audit.id))

    return render_template("admin_audit_detail.html", audit=audit)