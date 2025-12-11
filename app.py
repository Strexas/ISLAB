import os
from flask import Flask
from subsystems.user_management.routes import user_management_bp as user_management_blueprint
from subsystems.payment.routes import payment_bp
from subsystems.reservation_subsystem.routes import reservation_blueprint

from subsystems.maintenance_subsystem.routes import maintenance_subsystem_blueprint

from flask_migrate import Migrate

from context import db, mail
# Blueprints
from subsystems.fleet_management.routes import fleet_bp
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
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:1223334444@localhost:5432/car_rental_lab"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# INITIALIZE EXTENSIONS
db.init_app(app)
mail.init_app(app)
migrate = Migrate(app, db)

# REGISTER BLUEPRINTS
app.register_blueprint(dot_bp)
app.register_blueprint(fleet_bp)
app.register_blueprint(reservation_blueprint)
app.register_blueprint(user_management_bp)
app.register_blueprint(payment_bp)

app.template_folder = "templates"

if __name__ == '__main__':
    app.register_blueprint(maintenance_subsystem_blueprint)
    app.run(debug=True)
