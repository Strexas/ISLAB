from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from subsystems.reservation_subsystem.reservation_subsystem import ReservationSubsystem
from models.Vehicle import Vehicle
from models.User import User

reservation_blueprint = Blueprint("reservations", __name__)
reservation_subsystem = ReservationSubsystem()

@reservation_blueprint.route("/", methods=["GET"])
def index():
    return render_template("index.html", logged_in=('user_id' in session))

@reservation_blueprint.route("/reservations/reserve/<int:vehicle_id>", methods=["GET", "POST"])
def reserve(vehicle_id):
    # User must be logged in to reserve a vehicle
    if 'user_id' not in session:
        flash("You must be logged in to reserve a vehicle.", "error")
        return redirect(url_for("user_management.login"))

    # Fetch user details
    user = User.query.get(session['user_id'])

    # Fetch vehicle details
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # If form submitted, process reservation
    if request.method == "POST":
        # Create initial reservation
        reservation = reservation_subsystem.create_reservation(
            user=user,
            vehicle=vehicle,
            pickup_date=request.form.get("pickup_date"),
            return_date=request.form.get("return_date")
        )

        #Call Payment Subsystem to process payment here

        # if wants_insurance := request.form.get("wants_insurance"):
        #     reservation_subsystem.add_insurance(reservation)

        pass


    return render_template("car_reserve.html", logged_in=('user_id' in session), vehicle=vehicle, user=user)
