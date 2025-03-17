from app import db

# Datenbankmodell
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    otp_secret = db.Column(db.String(255), nullable=False)
    two_factor_enabled = db.Column(db.Boolean, default=False, nullable=False)
    two_factor_verified = db.Column(db.Boolean, default=False, nullable=False)
    is_superuser = db.Column(db.Boolean, default=False, nullable=False)
    account_locked = db.Column(db.Boolean, default=False, nullable=False)