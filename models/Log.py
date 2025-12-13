from context import db
from datetime import datetime

class Log(db.Model):
    __tablename__ = 'log'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )

    log = db.Column(db.String(255), nullable=False)

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
