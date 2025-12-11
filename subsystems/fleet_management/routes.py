from flask import (
    Blueprint, render_template, request,
    redirect, url_for, flash, session, current_app
)
from werkzeug.utils import secure_filename
import os
from datetime import date
import requests
from datetime import datetime, timedelta

from context import db
from models.Vehicle import Vehicle
from models.RentPrice import RentPrice
from models.ReviewCache import ReviewCache
from form.VehicleForm import VehicleForm, RetireVehicleForm


fleet_bp = Blueprint("fleet", __name__, url_prefix="/fleet")

# Allowed file extensions for vehicle image upload
ALLOWED_IMG = {"png", "jpg", "jpeg"}


# -------------------- UTILS --------------------

def allowed(filename):
    """Check if uploaded file has a valid image extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMG


def can_manage():
    """Employees + accountants can modify fleet."""
    return session.get("role") in ["employee", "accountant"]


# -------------------- LIST VEHICLES --------------------

@fleet_bp.route("/")
def fleet_list():
    vehicles = Vehicle.query.order_by(Vehicle.id).all()
    return render_template("fleetlist.html", vehicles=vehicles)


# -------------------- VEHICLE DETAILS --------------------

@fleet_bp.route("/<int:vehicle_id>")
def fleet_details(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    reviews = get_vehicle_reviews(vehicle_id)

    return render_template(
        "fleet_detail.html",
        vehicle=vehicle,
        reviews=reviews.get("reviews", [])
    )


# -------------------- ADD VEHICLE --------------------

@fleet_bp.route("/add", methods=["GET", "POST"])
def fleet_add():
    if not can_manage():
        flash("Access denied.", "danger")
        return redirect(url_for("fleet.fleet_list"))

    form = VehicleForm()

    if form.validate_on_submit():

        # Create vehicle
        vehicle = Vehicle(
            license_plate=form.license_plate.data,
            manufacturer=form.manufacturer.data,
            model=form.model.data,
            year=form.year.data,
            transmission=form.transmission.data,
            seats=form.seats.data,
            fuel_type=form.fuel_type.data,
            status=form.status.data
        )

        # ---------- IMAGE UPLOAD ----------
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

        # Save vehicle so ID exists
        db.session.add(vehicle)
        db.session.flush()

        # ---------- INITIAL PRICE ----------
        price_entry = RentPrice(
            vehicle_id=vehicle.id,
            price=form.current_price.data,
            date=date.today()
        )
        db.session.add(price_entry)

        db.session.commit()

        flash("Vehicle added successfully.", "success")
        return redirect(url_for("fleet.fleet_list"))

    return render_template("vehicle_form.html", form=form, mode="add")
    

# -------------------- EDIT VEHICLE --------------------

@fleet_bp.route("/<int:vehicle_id>/edit", methods=["GET", "POST"])
def fleet_edit(vehicle_id):
    if not can_manage():
        flash("Access denied.", "danger")
        return redirect(url_for("fleet.fleet_list"))

    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = VehicleForm()

    # ------------- LOAD EXISTING DATA -------------
    if request.method == "GET":
        form.license_plate.data = vehicle.license_plate
        form.manufacturer.data = vehicle.manufacturer
        form.model.data = vehicle.model
        form.year.data = vehicle.year
        form.transmission.data = vehicle.transmission
        form.seats.data = vehicle.seats
        form.fuel_type.data = vehicle.fuel_type
        form.status.data = vehicle.status
        form.current_price.data = vehicle.current_price() or 0

    # ------------- SUBMIT CHANGES -------------
    if form.validate_on_submit():

        vehicle.license_plate = form.license_plate.data
        vehicle.manufacturer = form.manufacturer.data
        vehicle.model = form.model.data
        vehicle.year = form.year.data
        vehicle.transmission = form.transmission.data
        vehicle.seats = form.seats.data
        vehicle.fuel_type = form.fuel_type.data
        vehicle.status = form.status.data

        # PRICE CHANGE? Create new RentPrice
        new_price = form.current_price.data
        if vehicle.current_price() != new_price:
            new_price_entry = RentPrice(
                vehicle_id=vehicle.id,
                price=new_price,
                date=date.today()
            )
            db.session.add(new_price_entry)

        # IMAGE UPDATE
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
        return redirect(url_for("fleet.fleet_details", vehicle_id=vehicle.id))

    return render_template("vehicle_form.html", form=form, mode="edit", vehicle=vehicle)


# -------------------- DELETE VEHICLE --------------------

@fleet_bp.route("/<int:vehicle_id>/delete", methods=["POST"])
def fleet_delete(vehicle_id):
    if session.get("role") != "accountant":
        flash("Only accountants can delete vehicles.", "danger")
        return redirect(url_for("fleet.fleet_list"))

    vehicle = Vehicle.query.get_or_404(vehicle_id)

    db.session.delete(vehicle)
    db.session.commit()

    flash("Vehicle deleted.", "success")
    return redirect(url_for("fleet.fleet_list"))

def get_vehicle_reviews(vehicle_id):
    """Returns reviews via cache or external API."""
    
    # ---- 1. Check cache ----
    cache = ReviewCache.query.filter_by(vehicle_id=vehicle_id).first()

    if cache:
        age = datetime.utcnow() - cache.fetched_at
        if age < timedelta(hours=24):  # Cache still valid
            return cache.data

    # ---- 2. Fetch from external API ----
    try:
        api_url = f"https://dummyjson.com/products/{vehicle_id}/reviews"
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()

        data = response.json()

        # ---- 3. Save new cache ----
        if cache:
            cache.data = data
            cache.fetched_at = datetime.utcnow()
        else:
            cache = ReviewCache(
                vehicle_id=vehicle_id,
                data=data,
                fetched_at=date.utcnow()
            )
            db.session.add(cache)

        db.session.commit()

        return data

    except Exception as e:
        print("Review API error:", e)
        return {"reviews": []}  # fallback

# Retire Vehicle
@fleet_bp.route('/<string:vehicle_id>/retire', methods=['GET', 'POST'])
def retire_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = RetireVehicleForm()
    
    if form.validate_on_submit():
        try:
            if not form.confirm.data:
                flash('Please confirm the retirement', 'error')
                return render_template('fleet_management/retire_vehicle.html', form=form, vehicle=vehicle)
            
            # Update vehicle status
            vehicle.status = 'Inactive'
            vehicle.updated_at = datetime.utcnow()
            
            # In a real system, you might want to store retirement details in a separate table
            db.session.commit()
            
            flash(f'Vehicle {vehicle.manufacturer} {vehicle.model} has been retired.', 'success')
            return redirect(url_for('fleet_management.fleet_list'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error retiring vehicle: {str(e)}', 'error')
    
    return render_template('fleet_management/retire_vehicle.html', form=form, vehicle=vehicle)
