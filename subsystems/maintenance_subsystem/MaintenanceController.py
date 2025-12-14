from context import db

from models.Maintenance import Maintenance
from models.Order import Order
from models.Component import Component
from models.Vehicle import Vehicle

class MaintenanceController:
    def __init__(self):
        pass

    @staticmethod
    def list_maintenances():
        maintenances = Maintenance.query.all()
        return maintenances

    @staticmethod
    def list_orders(maintenance_id):
        orders = Order.query.filter_by(id=maintenance_id).all()
        return orders

    @staticmethod
    def list_components(order_id):
        components = Component.query.filter_by(id=order_id).all()
        return components

    @staticmethod
    def get_vehicle_by_id(vehicle_id):
        vehicle = Vehicle.query.filter_by(id=vehicle_id).first()
        return vehicle

    @staticmethod
    def add_maintenance(model: str, plate: str, date):
        if not model and not plate:
            return "Model or Plate must be provided."

        if not model and plate:
            vehicles = Vehicle.query.filter_by(license_plate=plate).all()
        elif not plate and model:
            vehicles = Vehicle.query.filter_by(model=model).all()
        else:
            vehicles = Vehicle.query.filter_by(license_plate=plate, model=model).all()

        if len(vehicles) == 0:
            return "No vehicle found."

        if len(vehicles) > 1:
            return "More than one vehicle found."

        vehicle = vehicles[0]
        maintenance = Maintenance()
        if date:
            maintenance.start_date = date
        maintenance.vehicle_id = vehicle.id
        db.session.add(maintenance)
        db.session.commit()

        return "Successfully added maintenance."
