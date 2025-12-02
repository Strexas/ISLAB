from flask import Blueprint, render_template, session
from subsystems.reservation_subsystem.reservation_subsystem import ReservationSubsystem

reservation_blueprint = Blueprint("reservations", __name__)
reservation_subsystem = ReservationSubsystem()

@reservation_blueprint.route("/", methods=["GET"])
def index():
    return render_template("index.html", logged_in=('user_id' in session))

@reservation_blueprint.route("/fleetlist", methods=["GET"])
def fleet_list():
    return render_template("fleetlist.html", logged_in=('user_id' in session))

@reservation_blueprint.route("/car_details/<int:vehicle_id>", methods=["GET"])
def car_details(vehicle_id):
    return render_template("car_details.html", vehicle_id=vehicle_id)
