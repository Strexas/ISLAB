from datetime import date

from context import db

class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)

    maintenance_id = db.Column(db.Integer,
                               db.ForeignKey('maintenances.id', ondelete="CASCADE", onupdate="CASCADE"),
                               nullable=False)

    components = db.relationship("Component", backref="order")