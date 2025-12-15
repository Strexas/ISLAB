from datetime import date

from context import db

class Maintenance(db.Model):
    __tablename__ = "maintenances"

    id = db.Column(db.Integer, primary_key=True)

    maintenance_description = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    reported_problem = db.Column(db.String(255), nullable=True)

    vehicle_id = db.Column(db.Integer,
                           db.ForeignKey('vehicles.id', ondelete="CASCADE", onupdate="CASCADE"),
                           nullable=False)

    orders = db.relationship("Order", backref="maintenance")
