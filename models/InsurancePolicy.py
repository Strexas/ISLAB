from context import db

class InsurancePolicy(db.Model):
    __tablename__ = 'insurance_policie'

    insurance_id = db.Column(db.String(36), primary_key=True)
    reservation_id = db.Column(db.String(36), db.ForeignKey('reservations.reservation_id'), nullable=False)
    provider = db.Column(db.String(100), nullable=False)
    payment_amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    policy_number = db.Column(db.String(50), unique=True, nullable=False)