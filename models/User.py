from context import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    driver_license = db.Column(db.String(50))
    role = db.Column(db.String(20), default='customer')
    is_banned = db.Column(db.Boolean, default=False)

    # CREATION
    @staticmethod
    def create_user(email, password):
        user = User(email=email)
        user.password_hash = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        return user

    # AUTHENTICATION
    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()
        if user and not user.is_banned and check_password_hash(user.password_hash, password):
            return user
        return None

    # HELPERS
    @staticmethod
    def get_current():
        uid = session.get("user_id")
        return User.query.get(uid) if uid else None

    @staticmethod
    def get_by_id(user_id):
        return User.query.get_or_404(user_id)

    @staticmethod
    def get_all():
        return User.query.all()

    # ACCOUNT MANAGEMENT
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def ban(self):
        self.is_banned = True
        db.session.commit()

    def unban(self):
        self.is_banned = False
        db.session.commit()

    def update_license(self, license_value):
        self.driver_license = license_value
        db.session.commit()
