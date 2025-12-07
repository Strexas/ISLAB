from context import db
from datetime import datetime, timedelta
import secrets

class Token(db.Model):
    __tablename__ = 'tokens'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(128), unique=True, nullable=False)
    type = db.Column(db.String(50), default="verify_email")  # verify_email, reset_password, etc.
    expires_at = db.Column(db.DateTime, nullable=False)

    @staticmethod
    def generate(user_id, type="verify_email", hours_valid=24):
        token_value = secrets.token_urlsafe(32)

        t = Token(
            user_id=user_id,
            token=token_value,
            type=type,
            expires_at=datetime.utcnow() + timedelta(hours=hours_valid)
        )

        db.session.add(t)
        db.session.commit()
        return token_value

    def is_valid(self):
        return datetime.utcnow() < self.expires_at
