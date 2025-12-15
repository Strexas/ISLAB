from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from context import db

from form.VehicleForm import VehicleForm, RetireVehicleForm, ReviewCacheForm
from controllers.FleetController import FleetController

fleet_bp = Blueprint("fleet", __name__, url_prefix="/fleet")

# ----------------- PERMISSION -----------------

def can_manage():
    return session.get("role") in ["employee", "accountant"]

# ----------------- LIST VEHICLES -----------------

@fleet_bp.route("/")
def fleet_list():
    vehicles = FleetController.get_all_vehicles()
    return render_template("fleetlist.html", vehicles=vehicles)

# ----------------- VEHICLE DETAILS -----------------

@fleet_bp.route("/<int:vehicle_id>")
def vehicle_details(vehicle_id):
    vehicle = FleetController.get_vehicle(vehicle_id)
    reviews = FleetController.get_reviews(vehicle_id)

    return render_template(
        "car_details.html",
        vehicle=vehicle,
        rent_price=vehicle.rent_price,
        review_cache=vehicle.review_cache,
        reviews=reviews
    )

# ----------------- ADD VEHICLE -----------------

@fleet_bp.route("/add", methods=["GET", "POST"])
def fleet_add():
    if not can_manage():
        flash("Access denied.", "danger")
        return redirect(url_for("fleet.fleet_list"))

    form = VehicleForm()

    if form.validate_on_submit():
        file = request.files.get("image")
        FleetController.create_vehicle(form, file)
        flash("Vehicle added successfully.", "success")
        return redirect(url_for("fleet.fleet_list"))

    return render_template("add_car.html", form=form, mode="add")

# ----------------- EDIT VEHICLE -----------------

@fleet_bp.route("/<int:vehicle_id>/edit", methods=["GET", "POST"])
def fleet_edit(vehicle_id):
    if not can_manage():
        flash("Access denied.", "danger")
        return redirect(url_for("fleet.fleet_list"))

    vehicle = FleetController.get_vehicle(vehicle_id)
    form = VehicleForm()

    if request.method == "GET":
        form.license_plate.data = vehicle.license_plate
        form.manufacturer.data = vehicle.manufacturer
        form.model.data = vehicle.model
        form.year.data = vehicle.year
        form.transmission.data = vehicle.transmission
        form.seats.data = vehicle.seat
        form.fuel_type.data = vehicle.fuel_type
        form.status.data = vehicle.status
        form.current_price.data = vehicle.current_price()

    if form.validate_on_submit():
        file = request.files.get("image")
        FleetController.update_vehicle(vehicle, form, file)
        flash("Vehicle updated successfully.", "success")
        return redirect(url_for("fleet.fleet_details", vehicle_id=vehicle.id))

    return render_template("vehicle_form.html", form=form, mode="edit", vehicle=vehicle)

# ----------------- RETIRE VEHICLE -----------------

@fleet_bp.route("/<int:vehicle_id>/retire", methods=["GET", "POST"])
def retire_vehicle(vehicle_id):
    vehicle = FleetController.get_vehicle(vehicle_id)
    form = RetireVehicleForm()

    if form.validate_on_submit():
        if not form.confirm.data:
            flash("Please confirm retirement.", "danger")
            return render_template("retire_vehicle.html", form=form, vehicle=vehicle)

        FleetController.retire_vehicle(vehicle)
        flash("Vehicle retired.", "success")
        return redirect(url_for("fleet.fleet_list"))

    return render_template("retire_vehicle.html", form=form, vehicle=vehicle)

# ----------------- REVIEW CACHE -----------------

@fleet_bp.route("/<int:vehicle_id>/reviews", methods=["GET", "POST"])
def update_reviews(vehicle_id):
    vehicle = FleetController.get_vehicle(vehicle_id)
    form = ReviewCacheForm()

    if form.validate_on_submit():
        FleetController.update_review_cache(vehicle_id, form)
        flash("Review cache updated.", "success")
        return redirect(url_for("fleet.vehicle_details", vehicle_id=vehicle_id))

    return render_template("update_reviews.html", form=form, vehicle=vehicle)
