from context import db
from models.Vehicle import Vehicle
from models.RentPrice import RentPrice
from models.ReviewCache import ReviewCache
from werkzeug.utils import secure_filename
from datetime import datetime, date, timedelta
import requests, os

class FleetController:

    @staticmethod
    def get_all_vehicles():
        return Vehicle.query.order_by(Vehicle.vehicle_id).all()

    @staticmethod
    def get_vehicle(vehicle_id):
        return Vehicle.query.get_or_404(vehicle_id)

    @staticmethod
    def add_vehicle(data, image_file, upload_folder):
        vehicle = Vehicle(
            license_plate=data["license_plate"],
            manufacturer=data["manufacturer"],
            model=data["model"],
            year=data["year"],
            transmission=data["transmission"],
            seat=data["seats"],
            fuel_type=data["fuel_type"],
            status=data["status"]
        )

        # Save before assigning FK relations
        db.session.add(vehicle)
        db.session.flush()

        # -------- IMAGE SAVE --------
        if image_file:
            filename = secure_filename(image_file.filename)
            unique = f"{vehicle.license_plate}_{filename}"
            path = os.path.join(upload_folder, unique)

            os.makedirs(upload_folder, exist_ok=True)
            image_file.save(path)

            vehicle.image_path = f"/static/vehicles/{unique}"

        # -------- INITIAL PRICE --------
        price = RentPrice(price=data["price"], date=date.today())
        vehicle.rent_price = price

        db.session.commit()
        return vehicle

    @staticmethod
    def update_vehicle(vehicle, data, image_file, upload_folder):

        # Update fields
        for field in [
            "license_plate", "manufacturer", "model", "year",
            "transmission", "seats", "fuel_type", "status"
        ]:
            setattr(vehicle, field if field != "seats" else "seat", data[field])

        # -------- Price Update --------
        if vehicle.rent_price:
            vehicle.rent_price.price = data["price"]
            vehicle.rent_price.date = date.today()
        else:
            vehicle.rent_price = RentPrice(
                price=data["price"],
                date=date.today()
            )

        # -------- Image Update --------
        if image_file:
            filename = secure_filename(image_file.filename)
            unique = f"{vehicle.license_plate}_{filename}"
            path = os.path.join(upload_folder, unique)

            os.makedirs(upload_folder, exist_ok=True)
            image_file.save(path)

            vehicle.image_path = f"/static/vehicles/{unique}"

        db.session.commit()
        return vehicle

    @staticmethod
    def retire(vehicle):
        vehicle.status = "Inactive"
        vehicle.updated_at = datetime.utcnow()
        db.session.commit()
        return True

    @staticmethod
    def get_reviews(vehicle_id):

        cache = ReviewCache.query.filter_by(vehicle_id=vehicle_id).first()
        now = datetime.utcnow()

        if cache and now - cache.fetched_at < timedelta(hours=24):
            return cache.data

        # Fetch external reviews
        try:
            url = f"https://dummyjson.com/products/{vehicle_id}/reviews"
            r = requests.get(url, timeout=5)
            data = r.json()

            if cache:
                cache.data = data
                cache.fetched_at = now
            else:
                cache = ReviewCache(
                    vehicle_id=vehicle_id,
                    data=data,
                    fetched_at=now
                )
                db.session.add(cache)

            db.session.commit()
            return data

        except:
            return {"reviews": []}

    @staticmethod
    def update_review_cache(vehicle_id, data):

        cache = ReviewCache.query.filter_by(vehicle_id=vehicle_id).first()

        if cache:
            cache.average_rating = data["average_rating"]
            cache.review_count = data["review_count"]
            cache.last_updated = data["last_updated"]
            cache.source = data["source"]
        else:
            cache = ReviewCache(
                vehicle_id=vehicle_id,
                average_rating=data["average_rating"],
                review_count=data["review_count"],
                last_updated=data["last_updated"],
                source=data["source"]
            )
            db.session.add(cache)

        db.session.commit()
        return cache

