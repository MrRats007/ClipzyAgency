from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(190), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class AuditRequest(db.Model):
    __tablename__ = "audit_requests"
    id = db.Column(db.Integer, primary_key=True)

    # Lead info
    name = db.Column(db.String(160), nullable=False)
    email = db.Column(db.String(190), nullable=False, index=True)
    phone = db.Column(db.String(60), nullable=True)

    brand = db.Column(db.String(200), nullable=True)         # business/brand name
    ig_handle = db.Column(db.String(120), nullable=True)     # @handle
    website = db.Column(db.String(240), nullable=True)

    goals = db.Column(db.Text, nullable=True)                # what they want
    budget = db.Column(db.String(80), nullable=True)         # optional
    services = db.Column(db.String(200), nullable=True)      # selected service

    # Admin workflow
    status = db.Column(db.String(40), default="New")         # New / Contacted / Qualified / Closed
    admin_notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)