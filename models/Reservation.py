import enum
from context import db

class ReservationStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Reservation(db.Model):
    __tablename__ = 'reservations'

    reservation_id = db.Column(db.String(36), primary_key=True)
    customer_id = db.Column(db.String(36), nullable=False)
    car_id = db.Column(db.String(36), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    pickup_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
