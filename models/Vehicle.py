import enum
from flask_sqlalchemy import SQLAlchemy;
from app import db

class VehicleStatus(enum.Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"

class Vehicle(db.Model):
    __tablename__ = 'vehicles'

    vehicle_id = db.Column(db.String(36), primary_key=True)
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    year = db.Column(db.Integer)
    seats = db.Column(db.Integer)
    fuel_type = db.Column(db.String(20))
    transmission = db.Column(db.String(20))
    price_per_day = db.Column(db.Float)
    status = db.Column(db.Enum(VehicleStatus), default=VehicleStatus.AVAILABLE)