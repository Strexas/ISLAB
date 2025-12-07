# Since you might have a central db in context, but let's check
# First try to import from context, otherwise create our own
try:
    from context import db
    print("Using db from context")
except ImportError:
    print("Creating new SQLAlchemy instance for fleet_management")
    from flask_sqlalchemy import SQLAlchemy
    db = SQLAlchemy()

from datetime import datetime

class Vehicle(db.Model):
    __tablename__ = 'vehicles'
    
    vehicle_id = db.Column(db.String, primary_key=True)
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    manufacturer = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Available')
    transmission = db.Column(db.String(20), nullable=False)
    seat = db.Column(db.Integer, nullable=False)
    fuel_type = db.Column(db.String(20), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # Economy, Sedan, SUV, Van, Luxury
    price_per_day = db.Column(db.Float, nullable=False)
    
    def __repr__(self):
        return f'<Vehicle {self.manufacturer} {self.model} ({self.license_plate})>'

class RentPrice(db.Model):
    __tablename__ = 'rent_prices'
    
    rent_price_id = db.Column(db.String, primary_key=True)
    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    vehicle_id = db.Column(db.String, db.ForeignKey('vehicles.vehicle_id'), nullable=False)
    
    def __repr__(self):
        return f'<RentPrice {self.price} for {self.vehicle_id}>'

class ReviewCache(db.Model):
    __tablename__ = 'review_caches'
    
    review_id = db.Column(db.String, primary_key=True)
    average_rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    last_updated = db.Column(db.Date, nullable=False)
    source = db.Column(db.String(100))
    vehicle_id = db.Column(db.String, db.ForeignKey('vehicles.vehicle_id'), nullable=False)
    
    def __repr__(self):
        return f'<ReviewCache for {self.vehicle_id}>'