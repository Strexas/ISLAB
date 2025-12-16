from context import db
from datetime import date
from sqlalchemy.dialects.sqlite import JSON

class ReviewCache(db.Model):
    __tablename__ = "review_cache"

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.vehicle_id"), unique=True)
    data = db.Column(JSON, nullable=True)  

    average_rating = db.Column(db.Float, nullable=False, default=0.0)
    review_count = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.Date, nullable=False, default=date.today())
    source = db.Column(db.String(80))

    vehicle = db.relationship("Vehicle", back_populates="review_cache")