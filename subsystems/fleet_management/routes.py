from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, current_app
)
from werkzeug.utils import secure_filename
import os
from datetime import date, datetime, timedelta
import requests

from context import db
from models.Vehicle import Vehicle
from models.RentPrice import RentPrice
from models.ReviewCache import ReviewCache
from form.VehicleForm import VehicleForm, RetireVehicleForm, ReviewCacheForm
from subsystems.fleet_management.FleetController import FleetController
from subsystems.reservation_subsystem.reservation_subsystem import ReservationSubsystem


fleet_bp = Blueprint("fleet", __name__, url_prefix="/fleet")

ALLOWED_IMG = {"png", "jpg", "jpeg"}

# -------------------- UTILS --------------------

def allowed(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMG

def can_manage():
    return session.get("role") in ["employee", "accountant"]

# ----------------- LIST VEHICLES -----------------

@fleet_bp.route("/")
def fleet_list():
    rs = ReservationSubsystem()

    #Get dates from index search
    pickup_date_str = request.args.get("pickup_date")
    dropoff_date_str = request.args.get("dropoff_date")
    
    vehicles = FleetController.get_all_vehicles()

    print(vehicles)

    final = []
    #Dates are requested
    if pickup_date_str and pickup_date_str != "" and dropoff_date_str and dropoff_date_str != "":
        print(pickup_date_str, dropoff_date_str)
        try:
            pickup_date, dropoff_date = rs.parse_dates(pickup_date_str, dropoff_date_str)

            #Check all the vehicles in the requested dates if they are available
            for vehicle in vehicles:
                if rs.is_car_available(vehicle.vehicle_id, pickup_date, dropoff_date):
                    final.append(vehicle)

            return render_template("fleetlist.html", vehicles=final, pickup_date=pickup_date, dropoff_date=dropoff_date)
        except Exception as e:
            flash(f"Invalid dates requested {e}", "error")
            final = vehicles    
    
    else:
        final = vehicles
        
    return render_template("fleetlist.html", vehicles=final)

# ----------------- VEHICLE DETAILS -----------------

# -------------------- VEHICLE DETAILS --------------------

@fleet_bp.route("/<int:vehicle_id>")
def vehicle_details(vehicle_id):
    vehicle = FleetController.get_vehicle(vehicle_id)
    reviews = FleetController.get_reviews(vehicle_id)

    try:
        rs = ReservationSubsystem()

        #Get dates from index search
        pickup_date_str = request.args.get("pickup_date")
        dropoff_date_str = request.args.get("dropoff_date")
        
        if pickup_date_str and pickup_date_str != "" and dropoff_date_str and dropoff_date_str != "":
            pickup_date, dropoff_date = rs.parse_dates(pickup_date_str, dropoff_date_str)

            return render_template(
                "car_details.html",
                vehicle=vehicle,
                rent_price=vehicle.rent_price[-1] if vehicle.rent_price else None,
                review_cache=vehicle.review_cache,
                reviews=reviews,
                pickup_date=pickup_date,
                dropoff_date=dropoff_date
            )
    except Exception as e:
        flash(f"invalid dates requested: {e}")

    return render_template(
        "car_details.html",
        vehicle=vehicle,
        rent_price=vehicle.rent_price[-1] if vehicle.rent_price else None,
        review_cache=vehicle.review_cache,
        reviews=reviews,
    )

# -------------------- ADD VEHICLE --------------------

@fleet_bp.route("/add", methods=["GET", "POST"])
def fleet_add():
    if not can_manage():
        flash("Access denied.", "danger")
        return redirect(url_for("fleet.fleet_list"))

    form = VehicleForm()

    if form.validate_on_submit():

        vehicle = Vehicle(
            license_plate=form.license_plate.data,
            manufacturer=form.manufacturer.data,
            model=form.model.data,
            year=form.year.data,
            transmission=form.transmission.data,
            seat=form.seats.data,
            fuel_type=form.fuel_type.data,
            status=form.status.data
        )

        # ---------- IMAGE ----------
        file = request.files.get("image")
        if file and file.filename and allowed(file.filename):
            filename = secure_filename(file.filename)
            unique = f"{vehicle.license_plate}_{filename}"
            upload_path = os.path.join(
                current_app.root_path, "static", "vehicles", unique
            )
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)
            vehicle.image_path = f"/static/vehicles/{unique}"

        db.session.add(vehicle)
        db.session.flush()  # get vehicle_id

        # ---------- INITIAL PRICE (FIXED) ----------
        price = RentPrice(
            price=form.current_price.data,
            date=date.today()
        )
        vehicle.rent_price.append(price)
        db.session.add(price)

        db.session.commit()

        flash("Vehicle added successfully.", "success")
        return redirect(url_for("fleet.fleet_list"))

    return render_template("add_car.html", form=form, mode="add")

# -------------------- EDIT VEHICLE --------------------

@fleet_bp.route("/<int:vehicle_id>/edit", methods=["GET", "POST"])
def fleet_edit(vehicle_id):
    if not can_manage():
        flash("Access denied.", "danger")
        return redirect(url_for("fleet.fleet_list"))

    vehicle = FleetController.get_vehicle(vehicle_id)
    form = VehicleForm()

    # ---------- LOAD DATA ----------
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

    # ---------- SUBMIT ----------
    if form.validate_on_submit():

        vehicle.license_plate = form.license_plate.data
        vehicle.manufacturer = form.manufacturer.data
        vehicle.model = form.model.data
        vehicle.year = form.year.data
        vehicle.transmission = form.transmission.data
        vehicle.seat = form.seats.data
        vehicle.fuel_type = form.fuel_type.data
        vehicle.status = form.status.data

        # ---------- PRICE CHANGE (FIXED) ----------
        last_price = vehicle.rent_price[-1] if vehicle.rent_price else None
        if not last_price or last_price.price != form.current_price.data:
            new_price = RentPrice(
                price=form.current_price.data,
                date=date.today()
            )
            vehicle.rent_price.append(new_price)
            db.session.add(new_price)

        # ---------- IMAGE ----------
        file = request.files.get("image")
        if file and file.filename and allowed(file.filename):
            filename = secure_filename(file.filename)
            unique = f"{vehicle.license_plate}_{filename}"
            upload_path = os.path.join(
                current_app.root_path, "static", "vehicles", unique
            )
            os.makedirs(os.path.dirname(upload_path), exist_ok=True)
            file.save(upload_path)
            vehicle.image_path = f"/static/vehicles/{unique}"

        db.session.commit()

        flash("Vehicle updated successfully.", "success")
        return redirect(url_for("fleet.vehicle_details", vehicle_id=vehicle.vehicle_id))

    return render_template("add_car.html", form=form, mode="edit", vehicle=vehicle)

# -------------------- REVIEW CACHE --------------------

def get_vehicle_reviews(vehicle_id):
    cache = ReviewCache.query.filter_by(vehicle_id=vehicle_id).first()

    if cache:
        age = datetime.utcnow() - cache.fetched_at
        if age < timedelta(hours=24):
            return cache.data

    try:
        response = requests.get(
            f"https://dummyjson.com/products/{vehicle_id}/reviews",
            timeout=5
        )
        response.raise_for_status()
        data = response.json()

        if cache:
            cache.data = data
            cache.fetched_at = datetime.utcnow()
        else:
            cache = ReviewCache(
                vehicle_id=vehicle_id,
                data=data,
                fetched_at=datetime.utcnow()
            )
            db.session.add(cache)

        db.session.commit()
        return data

    except Exception:
        return {"reviews": []}

# -------------------- RETIRE VEHICLE --------------------

@fleet_bp.route("/<string:vehicle_id>/retire", methods=["GET", "POST"])
def retire_vehicle(vehicle_id):
    if not can_manage():
        flash("Access denied.", "danger")
        return redirect(url_for("fleet.fleet_list"))
    vehicle = FleetController.get_vehicle(vehicle_id)
    form = RetireVehicleForm()

    # Handle confirmation submit
    if form.validate_on_submit():
        if not form.confirm.data:
            flash("Please confirm retirement.", "warning")
            return render_template("retire_vehicle.html", form=form, vehicle=vehicle)

        # Use controller method
        FleetController.retire(vehicle)

        flash("Vehicle retired successfully.", "success")
        return redirect(url_for("fleet.fleet_list"))

    return render_template("retire_vehicle.html", form=form, vehicle=vehicle)

@fleet_bp.route("/<int:vehicle_id>/delete", methods=["POST"])
def fleet_delete(vehicle_id):
    if session.get("role") != "accountant":
        flash("Access denied.", "danger")
        return redirect(url_for("fleet.fleet_list"))

    vehicle = Vehicle.query.get_or_404(vehicle_id)

    db.session.delete(vehicle)
    db.session.commit()

    flash("Vehicle deleted successfully.", "success")
    return redirect(url_for("fleet.fleet_list"))