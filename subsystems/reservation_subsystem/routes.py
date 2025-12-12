from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.Vehicle import Vehicle
from subsystems.reservation_subsystem.reservation_subsystem import ReservationSubsystem

reservation_blueprint = Blueprint("reservations", __name__)
reservation_subsystem = ReservationSubsystem()

@reservation_blueprint.route("/", methods=["GET"])
def index():
    return render_template("index.html", logged_in=('user_id' in session))

# @reservation_blueprint.route("/fleetlist", methods=["GET"])
# def fleet_list():
#     #Get all cars from the database
#     cars = Vehicle.query.all()
#     fleet = [c.to_dict() for c in cars]

#     return render_template("fleetlist.html", logged_in=('user_id' in session), fleet=fleet)

# @reservation_blueprint.route("/car_details/<int:vehicle_id>", methods=["GET"])
# def car_details(vehicle_id):
#     #Get info for the car with vehicle_id from the database
#     # car = Car.query.get(vehicle_id)
#     # if not car:
#     #     return "Car not found", 404
    
#     return render_template("car_details.html", logged_in=('user_id' in session))

# @reservation_blueprint.route("/reserve", methods=["GET"])
# def reserve():
#     #Check if user is logged in
#     # if "user_id" not in session:
#     #     flash("You must be logged in to reserve a car.", "error")
#     #     return redirect(url_for("user_management.login"))
    
#     # user_id = session["user_id"]
#     #Get from the form
#     car_id = "s"
#     pickup_date_str = request.form.get("pickup_date")
#     return_date_str = request.form.get("return_date")
#     wants_insurance = request.form.get("wants_insurance") == "on"

#     #Validate inputs
#     try:
#         pickup_date, return_date = reservation_subsystem.parse_dates(pickup_date_str, return_date_str)
#     except ValueError as e:
#         flash(str(e), "error")
#         #Redirect back to the reservation page
#         return redirect(request.referrer or url_for("reservations.fleet_list"))

#     #Try to get the car being reserved
#     # car = Car.query.get(car_id)
#     # if not car:
#     #     flash("Selected car does not exist.", "error")
#     #     return redirect(request.referrer or url_for("reservations.fleet_list"))

#     #Check car availability
#     if not reservation_subsystem.is_car_available(car_id, pickup_date, return_date):
#         # Show car unavailable message
#         flash("Sorry, this car is not available for the selected dates.", "error")
#         return redirect(request.referrer or url_for("reservations.fleet_list"))

#     # --- 5. Optional: create insurance ---
#     insurance_policy = None
#     if wants_insurance:
#         insurance_policy = reservation_subsystem.create_insurance_policy(
#             user_id=user_id,
#             car_id=car_id,
#             pickup_date=pickup_date,
#             return_date=return_date,
#         )

#     return render_template("car_reserve.html", logged_in=('user_id' in session))

