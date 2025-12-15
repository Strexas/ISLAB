import os
from flask import Flask
from flask_migrate import Migrate

from context import db, mail
# Blueprints
from subsystems.user_management.routes import user_management_bp
from subsystems.reservation_subsystem.routes import reservation_blueprint
from subsystems.user_management.dot_service import dot_bp

app = Flask(__name__)

# SECRET KEY
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# MAILTRAP SETTINGS
app.config['MAIL_SERVER'] = "sandbox.smtp.mailtrap.io"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "3ff460c1082e82"
app.config['MAIL_PASSWORD'] = "f6cd02818d6de8"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:Mariaajo8!@localhost:5432/islab_berku"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INITIALIZE EXTENSIONS
db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)

# REGISTER BLUEPRINTS
app.register_blueprint(dot_bp)
app.register_blueprint(user_management_bp)
app.register_blueprint(reservation_blueprint)

from models.User import User
from context import db
from werkzeug.security import generate_password_hash

def create_default_admin():
    admin_email = "admin@carrenting.com"
    admin_password = "admin123"

    existing = User.query.filter_by(email=admin_email).first()
    if existing:
        return

    admin = User(
        email=admin_email,
        name="System",
        surname="Admin",
        role="accountant",      
        account_status=True,
        is_verified=True,
        is_banned=False
    )
    admin.set_password(admin_password)

    db.session.add(admin)
    db.session.commit()
    print("Default admin created")

with app.app_context():
    create_default_admin()

from models.Reservation import Reservation
from models.InsurancePolicy import InsurancePolicy
from models.User import User

if __name__ == '__main__':
    app.run(debug=True)
