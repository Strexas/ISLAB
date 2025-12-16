import os
from flask import Flask
from flask_migrate import Migrate

from context import db, mail

from models.User import User

# Blueprints
from subsystems.user_management.routes import user_management_bp
from subsystems.reservation_subsystem.routes import reservation_blueprint
from subsystems.maintenance_subsystem.routes import maintenance_bp
from subsystems.payment.routes import payment_bp
from subsystems.fleet_management.routes import fleet_bp



app = Flask(__name__)

# SECRET KEY
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# MAILTRAP SETTINGS
app.config['MAIL_SERVER'] = "sandbox.smtp.mailtrap.io"
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = "06bd0b75a26d96"
app.config['MAIL_PASSWORD'] = "b7cab03071658e"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

# DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:1223334444@localhost:5432/car_rental_lab"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INITIALIZE EXTENSIONS
db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)

# REGISTER BLUEPRINTS
app.register_blueprint(fleet_bp)
app.register_blueprint(reservation_blueprint)
app.register_blueprint(user_management_bp)
app.register_blueprint(payment_bp)
app.register_blueprint(maintenance_bp)

app.template_folder = "templates"

# def create_default_admin():
#     admin_email = "admin@carrenting.com"
#     admin_password = "admin123"

#     existing = User.query.filter_by(email=admin_email).first()
#     if existing:
#         return

#     admin = User(
#         email=admin_email,
#         name="system",
#         surname="admin",
#         role="accountant",
#         account_status=True,
#         is_verified=True,
#         is_banned=False
#     )
#     admin.set_password(admin_password)

#     db.session.add(admin)
#     db.session.commit()
#     print("default admin created")

# with app.app_context():
#     create_default_admin()

if __name__ == '__main__':
    app.run(debug=True)
