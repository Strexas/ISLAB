import os


from flask import Flask
from subsystems.user_management.routes import user_management_bp as user_management_blueprint
from subsystems.reservation_subsystem.routes import reservation_blueprint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from context import db

app = Flask(__name__)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://db_user:2@localhost:5432/car_rental"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.register_blueprint(user_management_blueprint)
app.register_blueprint(reservation_blueprint)

if __name__ == '__main__':
    app.run(debug=True)

from models.Reservation import Reservation as Reservation
from models.InsurancePolicy import InsurancePolicy as InsurancePolicy
