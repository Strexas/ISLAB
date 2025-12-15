from context import db
from datetime import date

class RentPrice(db.Model):
    __tablename__ = "rent_price"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.vehicle_id"), unique=True)

    price = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

    vehicle = db.relationship("Vehicle", back_populates="rent_price")