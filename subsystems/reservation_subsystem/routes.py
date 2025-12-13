from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from subsystems.reservation_subsystem.reservation_subsystem import ReservationSubsystem
from models.Vehicle import Vehicle
from models.User import User
from models.Reservation import Reservation
from models.InsurancePolicy import InsurancePolicy

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
        try:
            # Create initial reservation
            reservation = reservation_subsystem.create_reservation(
                user=user,
                vehicle=vehicle,
                pickup_date_s=request.form.get("pickup_date"),
                return_date_s=request.form.get("return_date")
            )


            # If user opted for insurance, add it to the reservation
            wants_insurance = request.form.get("wants_insurance")
            if wants_insurance:
                
                reservation_subsystem.add_insurance_to_reservation(
                    reservation=reservation,
                    provider="Placeholder Provider",
                    amount=29.99
                )
                
            #Call Payment Subsystem to process payment here

            #If payment successful, finalize reservation
            reservation_subsystem.finalize_reservation(reservation)

            # Show success page
            return redirect(url_for("reservations.reservation_success", reservation_id=reservation.reservation_id))
        except Exception as ex:
            flash(ex, "error")
            return render_template("car_reserve.html", logged_in=('user_id' in session), vehicle=vehicle, user=user)

    return render_template("car_reserve.html", logged_in=('user_id' in session), vehicle=vehicle, user=user)

@reservation_blueprint.route("/reservations/success/<string:reservation_id>", methods=["GET"])
def reservation_success(reservation_id):
    # User must be logged to view reservation success
    if 'user_id' not in session:
        flash("You must be logged in to reserve a vehicle.", "error")
        return redirect(url_for("user_management.login"))


    #Fetch reservation details
    reservation = Reservation.query.get_or_404(reservation_id)
    insurnace_policy = InsurancePolicy.query.filter_by(reservation_id=reservation_id).first()
    vehicle = Vehicle.query.get_or_404(reservation.vehicle_id)
    user = User.query.get(session['user_id'])

    return render_template("reservation_success.html", vehicle=vehicle, user=user, reservation=reservation, insurance_policy=insurnace_policy)
    
@reservation_blueprint.route("/reservations/delete/<int:reservation_id>")
def delete_reservation():
    