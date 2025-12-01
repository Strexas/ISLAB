from flask import Blueprint, render_template, session
from reservation_subsystem.reservation_subsystem import ReservationSubsystem;

reservation = Blueprint("reservations", __name__)
reservation_subsystem = ReservationSubsystem()

@reservation.route("/", methods=["GET"])
def index():
    return render_template("index.html", logged_in=('user_id' in session))

@reservation.route("/fleetlist", methods=["GET"])
def fleet_list():
    return render_template("fleetlist.html", logged_in=('user_id' in session))

@reservation.route("/car_details/<int:vehicle_id>", methods=["GET"])
def car_details(vehicle_id):
    return render_template("car_details.html", vehicle_id=vehicle_id)
