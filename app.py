from flask import Flask
from user_management.routes import user_management_bp as user_management_blueprint
from reservation_subsystem.routes import reservation_subsystem
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://db_user:2@localhost:5432/car_rental"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)

db.init_app(app)

app.register_blueprint(user_management_blueprint)
app.register_blueprint(reservation_subsystem)

if __name__ == '__main__':
    app.run(debug=True)


from models.Reservation import Reservation as Reservation
from models.InsurancePolicy import InsurancePolicy as InsurancePolicy