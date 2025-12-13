from context import db
from enum import Enum
from sqlalchemy import Enum as PgEnum
from datetime import datetime


class PaymentStatus(Enum):
    PENDING = "Pending"
    AUTHORIZED = "Authorized"
    SUCCESS = "Success"
    FAILED = "Failed"


class Payment(db.Model):
    __tablename__ = "payment"

    paymentid = db.Column(db.Integer, primary_key=True, autoincrement=True)

    userid = db.Column(db.Integer,
                       db.ForeignKey("users.id"),
                       nullable=False)

    reservationid = db.Column(db.Integer,
                              db.ForeignKey("reservations.reservation_id"),
                              nullable=True)

    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Float, nullable=False)

    status = db.Column(
        PgEnum(PaymentStatus, name="paymentstatus"),
        nullable=False,
        default=PaymentStatus.PENDING
    )

    paymentmethod = db.Column(db.String(20), nullable=False)  # "Card" / "Balance"
    description = db.Column(db.String(255), nullable=True)
