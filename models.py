# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    domain = db.Column(db.String(255), nullable=False)
    tool = db.Column(db.String(50), nullable=False)
    result = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    scan_id = db.Column(db.String(36), nullable=False)

    user = db.relationship('User', backref=db.backref('scan_results', lazy=True))