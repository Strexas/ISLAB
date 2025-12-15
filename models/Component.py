from datetime import date

from context import db

class Component(db.Model):
    __tablename__ = "components"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=True)
    quantity = db.Column(db.Integer, nullable=False)

    order_id = db.Column(db.Integer,
                         db.ForeignKey('orders.id', ondelete="CASCADE", onupdate="CASCADE"),
                         nullable=False)
