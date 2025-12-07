from context import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Datos personales (del UML)
    name = db.Column(db.String(120))
    surname = db.Column(db.String(120))
    birthdate = db.Column(db.Date, nullable=True)

    # Credenciales
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    # Rol y estado de cuenta
    role = db.Column(db.String(20), default='customer')  # customer, employee, accountant
    account_status = db.Column(db.Boolean, default=True)  # activa/inactiva (banned)

    # Verificación de email
    is_verified = db.Column(db.Boolean, default=False)

    # Datos de licencia
    driver_license = db.Column(db.String(50), nullable=True)
    license_expiration = db.Column(db.Date, nullable=True)
    license_verified = db.Column(db.Boolean, default=False)
    license_photo_path = db.Column(db.String(255))

    # ---- Helpers de contraseña ----
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ---- Creación y autenticación ----
    @staticmethod
    def create_user(email, password, name=None, surname=None, birthdate=None):
        user = User(
            email=email,
            name=name,
            surname=surname,
            birthdate=birthdate,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()
        if user and user.account_status and user.verify_password(password):
            return user
        return None

    # ---- Helpers de sesión ----
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

    # ---- Gestión de cuenta ----
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def ban(self):
        self.account_status = False
        db.session.commit()

    def unban(self):
        self.account_status = True
        db.session.commit()
