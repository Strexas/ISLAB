from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from context import db

# Models
from models.Vehicle import Vehicle, RentPrice, ReviewCache

# Forms
from form.VehicleForm import (
    VehicleForm,
    RentPriceForm,
    ReviewCacheForm,
    VehicleFilterForm,
    RetireVehicleForm
)

from datetime import datetime, date
import uuid

fleet_management_bp = Blueprint(
    "fleet_management",
    __name__,
    url_prefix="/fleet"
)

# Fleet List with Filtering
@fleet_management_bp.route('/', methods=['GET'])
def fleet_list():
    form = VehicleFilterForm()
    
    type_filter = request.args.get('type', '')
    min_seats = request.args.get('min_seats', type=int)
    max_price = request.args.get('max_price', type=float)
    fuel_type_filter = request.args.get('fuel_type', '')
    status_filter = request.args.get('status', '')

    query = Vehicle.query

    if type_filter:
        query = query.filter(Vehicle.type == type_filter)
    if min_seats:
        query = query.filter(Vehicle.seat >= min_seats)
    if max_price:
        query = query.filter(Vehicle.price_per_day <= max_price)
    if fuel_type_filter:
        query = query.filter(Vehicle.fuel_type == fuel_type_filter)
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    
    vehicles = query.order_by(Vehicle.manufacturer, Vehicle.model).all()

    return render_template('fleetlist.html',
                           vehicles=vehicles,
                           form=form,
                           current_filters=request.args)

# Vehicle Details
@fleet_management_bp.route('/<string:vehicle_id>', methods=['GET'])
def vehicle_details(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    current_rent_price = RentPrice.query.filter_by(vehicle_id=vehicle_id)\
        .order_by(RentPrice.date.desc()).first()

    review_cache = ReviewCache.query.filter_by(vehicle_id=vehicle_id).first()

    price_history = RentPrice.query.filter_by(vehicle_id=vehicle_id)\
        .order_by(RentPrice.date.desc()).limit(10).all()

    return render_template('car_details.html',
                           vehicle=vehicle,
                           current_rent_price=current_rent_price,
                           review_cache=review_cache,
                           price_history=price_history)

# Add New Vehicle
@fleet_management_bp.route('/add', methods=['GET', 'POST'])
def add_vehicle():
    form = VehicleForm()

    if form.validate_on_submit():
        try:
            new_vehicle = Vehicle(
                vehicle_id=form.vehicle_id.data,
                license_plate=form.license_plate.data,
                manufacturer=form.manufacturer.data,
                model=form.model.data,
                year=form.year.data,
                status=form.status.data,
                transmission=form.transmission.data,
                seat=form.seat.data,
                fuel_type=form.fuel_type.data,
                type=form.type.data,
                price_per_day=form.price_per_day.data,
                image_url=form.image_url.data,
                description=form.description.data
            )

            db.session.add(new_vehicle)

            initial_rent_price = RentPrice(
                rent_price_id=f"RP_{form.vehicle_id.data}_{datetime.utcnow().strftime('%Y%m%d')}",
                price=form.price_per_day.data,
                date=date.today(),
                vehicle_id=form.vehicle_id.data
            )

            db.session.add(initial_rent_price)
            db.session.commit()

            flash("Vehicle added successfully!", "success")
            return redirect(url_for('fleet_management.vehicle_details',
                                    vehicle_id=form.vehicle_id.data))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error adding vehicle: {e}", "error")

    return render_template('add_vehicle.html', form=form)

# Edit Vehicle
@fleet_management_bp.route('/<string:vehicle_id>/edit', methods=['GET', 'POST'])
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = VehicleForm(obj=vehicle)

    if form.validate_on_submit():
        try:
            vehicle.manufacturer = form.manufacturer.data
            vehicle.model = form.model.data
            vehicle.year = form.year.data
            vehicle.status = form.status.data
            vehicle.transmission = form.transmission.data
            vehicle.seat = form.seat.data
            vehicle.fuel_type = form.fuel_type.data
            vehicle.type = form.type.data
            vehicle.image_url = form.image_url.data
            vehicle.description = form.description.data

            if vehicle.price_per_day != form.price_per_day.data:
                vehicle.price_per_day = form.price_per_day.data

                new_record = RentPrice(
                    rent_price_id=f"RP_{vehicle.vehicle_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    price=form.price_per_day.data,
                    date=date.today(),
                    vehicle_id=vehicle.vehicle_id
                )
                db.session.add(new_record)

            db.session.commit()
            flash("Vehicle updated!", "success")
            return redirect(url_for('fleet_management.vehicle_details', vehicle_id=vehicle.vehicle_id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating vehicle: {e}", "error")

    return render_template('edit_vehicle.html', form=form, vehicle=vehicle)

# Retire Vehicle
@fleet_management_bp.route('/<string:vehicle_id>/retire', methods=['GET', 'POST'])
def retire_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = RetireVehicleForm()

    if form.validate_on_submit():
        try:
            vehicle.status = "Inactive"
            vehicle.updated_at = datetime.utcnow()

            db.session.commit()
            flash("Vehicle retired!", "success")
            return redirect(url_for('fleet_management.fleet_list'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error retiring vehicle: {e}", "error")

    return render_template('retire_vehicle.html', form=form, vehicle=vehicle)

# Update Reviews
@fleet_management_bp.route('/<string:vehicle_id>/update_reviews', methods=['GET', 'POST'])
def update_reviews(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    form = ReviewCacheForm()

    review = ReviewCache.query.filter_by(vehicle_id=vehicle_id).first()

    if form.validate_on_submit():
        try:
            if review:
                review.average_rating = form.average_rating.data
                review.review_count = form.review_count.data
                review.last_updated = form.last_updated.data
                review.source = form.source.data
            else:
                new_review = ReviewCache(
                    review_id=f"REV_{vehicle_id}_{datetime.utcnow().strftime('%Y%m%d')}",
                    average_rating=form.average_rating.data,
                    review_count=form.review_count.data,
                    last_updated=form.last_updated.data,
                    source=form.source.data,
                    vehicle_id=vehicle_id
                )
                db.session.add(new_review)

            db.session.commit()
            flash("Review cache updated!", "success")
            return redirect(url_for('fleet_management.vehicle_details', vehicle_id=vehicle_id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error updating reviews: {e}", "error")

    if review and request.method == 'GET':
        form.average_rating.data = review.average_rating
        form.review_count.data = review.review_count
        form.last_updated.data = review.last_updated
        form.source.data = review.source

    return render_template('update_reviews.html', form=form, vehicle=vehicle)
