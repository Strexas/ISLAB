from datetime import date

from context import db

class Maintenance(db.Model):
    __tablename__ = "maintenances"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(
        db.Integer, 
        db.ForeignKey('vehicles.vehicle_id', ondelete="CASCADE", onupdate="CASCADE"), 
        nullable=False)
    
    maintenance_description = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    reported_problem = db.Column(db.String(255), nullable=True)

    orders = db.relationship("Order", backref="maintenance")
