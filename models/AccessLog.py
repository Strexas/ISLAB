from context import db
from datetime import datetime


class AccessLog(db.Model):
    __tablename__ = 'access_logs'

    id = db.Column(db.Integer, primary_key=True)
    
    employee_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )

    action = db.Column(db.String(255))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
