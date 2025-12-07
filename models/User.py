from context import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask import session

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    # Datos personales
    name = db.Column(db.String(120))
    surname = db.Column(db.String(120))
    birthdate = db.Column(db.Date, nullable=True)

    # Credenciales
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)

    # Rol y estado
    role = db.Column(db.String(20), default='customer')       # customer, employee, accountant
    account_status = db.Column(db.Boolean, default=True)      # activa/inactiva
    is_banned = db.Column(db.Boolean, default=False)          # banned flag

    # Verificación email
    is_verified = db.Column(db.Boolean, default=False)

    # Licencia
    driver_license = db.Column(db.String(50), nullable=True)
    license_expiration = db.Column(db.Date, nullable=True)
    license_verified = db.Column(db.Boolean, default=False)
    license_photo_path = db.Column(db.String(255))

    # ---------------- RELACIONES (para cascade delete) ----------------
    logs = db.relationship(
        "AccessLog",
        backref="user",
        cascade="all, delete",
        passive_deletes=True
    )
    tokens = db.relationship(
    "Token",
    cascade="all, delete-orphan",
    passive_deletes=True
)


    # ---------------- Password helpers ----------------
    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    # ---------------- Crear usuario ----------------
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

    # ---------------- Autenticación ----------------
    @staticmethod
    def authenticate(email, password):
        user = User.query.filter_by(email=email).first()

        if not user:
            return None

        # Usuario baneado
        if user.is_banned:
            return "banned"

        # Usuario desactivado manualmente
        if not user.account_status:
            return "disabled"

        # Contraseña correcta
        if user.verify_password(password):
            return user

        return None

    # ---------------- Helpers de sesión ----------------
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

    # ---------------- Gestión de cuenta ----------------
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
