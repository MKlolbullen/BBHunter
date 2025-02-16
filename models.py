from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from config import Config

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    registered_on = db.Column(db.DateTime, server_default=db.func.now())

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(Config.SECRET_KEY, expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(Config.SECRET_KEY)
        try:
            user_id = s.loads(token)['user_id']
        except Exception:
            return None
        return User.query.get(user_id)

class ScanResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    domain = db.Column(db.String(255), nullable=False)
    tool = db.Column(db.String(50), nullable=False)
    result = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    scan_id = db.Column(db.String(36), nullable=False)

    user = db.relationship('User', backref=db.backref('scan_results', lazy=True))