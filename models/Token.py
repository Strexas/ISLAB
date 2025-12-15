from context import db
from datetime import datetime, timedelta
import secrets

class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="CASCADE"),
        nullable=False
    )

    token = db.Column(db.String(128), unique=True, nullable=False)
    type = db.Column(db.String(50), default="verify_email")  
    expires_at = db.Column(db.DateTime, nullable=False)

    def is_valid(self):
        return datetime.utcnow() < self.expires_at
