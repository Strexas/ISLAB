from context import db
from datetime import date

class Vehicle(db.Model):
    __tablename__ = "vehicles"

    vehicle_id = db.Column(db.Integer, primary_key=True)
    
    license_plate = db.Column(db.String(20), unique=True, nullable=False)
    manufacturer = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)

    status = db.Column(db.String(20), nullable=False, default="Available")

    transmission = db.Column(db.String(40))
    seat = db.Column(db.Integer)
    fuel_type = db.Column(db.String(40))

    # Extensión para almacenar foto (no afecta UML)
    image_path = db.Column(db.String(255))

    rent_price = db.relationship(
        "RentPrice",
        back_populates="vehicle",
        cascade="all, delete-orphan",
        order_by="RentPrice.date.desc()"
    )

    review_cache = db.relationship(
        "ReviewCache",
        back_populates="vehicle",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def current_price(self):
        if self.rent_prices:
            return self.rent_prices[0].price
        return 0.0