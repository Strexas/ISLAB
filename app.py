from flask import Flask
from user_management.routes import user_management_bp as user_management_blueprint
from reservation_subsystem.routes import reservation_subsystem
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

if __name__ == '__main__':
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://db_user:2@localhost:5432/car_rental"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    app.register_blueprint(user_management_blueprint)
    app.register_blueprint(reservation_subsystem)
    app.run(debug=True)
