import enum
from context import db

class ReservationStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Reservation(db.Model):
    __tablename__ = 'reservations'

    reservation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    pickup_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(ReservationStatus), default=ReservationStatus.PENDING, nullable=False)
