from context import db
from models.User import User
from flask import session
from werkzeug.security import generate_password_hash, check_password_hash
from models.Token import Token
from datetime import datetime, timedelta
import secrets
class UserManagementController:
    
    @staticmethod
    def generate_token(user_id, type="verify_email", hours_valid=1):
        Token.query.filter_by(
            user_id=user_id,
            type=type
        ).delete()

        token_value = secrets.token_urlsafe(32)

        token = Token(
            user_id=user_id,
            token=token_value,
            type=type,
            expires_at=datetime.utcnow() + timedelta(hours=hours_valid)
        )

        db.session.add(token)
        db.session.commit()
        return token_value

    @staticmethod
    def create_user(email, password, name=None, surname=None, birthdate=None, role="customer"):
        user = User(
            email=email,
            name=name,
            surname=surname,
            birthdate=birthdate,
            role=role,
            account_status=True,
            is_verified=False,
            is_banned=False
        )

        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()

        if not user:
            return None

        if user.is_banned:
            return "banned"

        if not user.account_status:
            return "disabled"

        if user.verify_password(password):
            return user

        return None

    @staticmethod
    def get_current():
        uid = session.get("user_id")
        return User.query.get(uid) if uid else None

    @staticmethod
    def get_by_id(user_id):
        return User.query.get_or_404(user_id)

    @staticmethod
    def get_all():
        return User.query.order_by(User.id).all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def ban(self):
        self.is_banned = True
        self.account_status = False
        db.session.commit()

    def unban(self):
        self.is_banned = False
        self.account_status = True
        db.session.commit()
