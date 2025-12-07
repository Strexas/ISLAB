from context import db
from datetime import date


class CreditCard(db.Model):
    __tablename__ = "creditcard"

    cardid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey("user.userid"), nullable=False)

    cardholdername = db.Column(db.String(100), nullable=False)
    cardnumber = db.Column(db.String(20), nullable=False)
    expiredate = db.Column(db.Date, nullable=False)
    billingaddress = db.Column(db.String(255), nullable=False)
    added = db.Column(db.Date, nullable=False, default=date.today)
