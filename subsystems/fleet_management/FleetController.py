from context import db
from models.Vehicle import Vehicle
from models.RentPrice import RentPrice
from models.ReviewCache import ReviewCache
from werkzeug.utils import secure_filename
from flask import session
from datetime import datetime, date, timedelta
import requests, os

FAKESTORE_MAP = {
    1: 1,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    # map your vehicle IDs to product IDs
}
class FleetController:

    @staticmethod
    def get_all_vehicles():
        # Customers: show only ACTIVE cars
        role = session.get("role")

        # Customers: show only ACTIVE cars
        if role not in ["employee", "accountant"]:
            return Vehicle.query.filter_by(status="Available").all()

        # Employees + accountants: show ALL cars
        return Vehicle.query.all()


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
    def retire(vehicle):
       vehicle.status = "Inactive"
       db.session.commit()
       return True
    

    @staticmethod
    def update_vehicle(vehicle, data, image_file, upload_folder):

        # Update fields
        for field in [
            "license_plate", "manufacturer", "model", "year",
            "transmission", "seat", "fuel_type", "status"
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
    def get_reviews(vehicle_id):
        cache = ReviewCache.query.filter_by(vehicle_id=vehicle_id).first()
        now = date.today()
        
        # 24h cache
        if cache and now - cache.last_updated < timedelta(days=3):
            return cache.data

        api_id = FAKESTORE_MAP.get(vehicle_id, 1)
        url = f"https://fakestoreapi.com/products/{api_id}"

        try:
            r = requests.get(url, timeout=10)
            r.raise_for_status()     # ← IMPORTANT
            data = r.json()

            rating = data.get("rating", {})
            avg = rating.get("rate", 0)
            count = rating.get("count", 0)


        # Make sure rating exists
            if "rating" not in data:
                data["rating"] = {"rate": 0, "count": 0}

            if cache:
                cache.data = data
                cache.last_updated = now
                cache.average_rating = avg
                cache.review_count = count
                cache.source = "FakeStoreAPI"
            else:
                cache = ReviewCache(
                 vehicle_id=vehicle_id,
                 data=data,
                 last_updated=now,
                 average_rating = avg,
                 review_count = count,
                 source="FakeStoreAPI"
                 
                )
                db.session.add(cache)

            db.session.commit()
            return data

        except Exception as e:
            print("API ERROR:", e)
            db.session.rollback()
            return {"rating": {"rate": 0, "count": 0}}
        

