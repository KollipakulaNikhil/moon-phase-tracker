from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    dob = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_calculation = db.Column(db.Date, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'dob': self.dob.strftime('%Y-%m-%d') if self.dob else None,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'last_calculation': self.last_calculation.strftime('%Y-%m-%d') if self.last_calculation else None
        }