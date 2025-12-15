""" Maintenance Controller"""

# pylint: disable=import-error
from context import db

from models.Maintenance import Maintenance
from models.Order import Order
from models.Component import Component
from models.Vehicle import Vehicle
#pylint: enable=import-error

class MaintenanceController:
    """ Controller for the maintenance subsystem. Handles all related operations."""
    def __init__(self):
        pass

    @staticmethod
    def list_maintenances():
        """
        List all maintenances.
        :return: List of all maintenances.
        """

        maintenances = Maintenance.query.all()
        return maintenances

    @staticmethod
    def get_maintenance_by_id(maintenance_id):
        maintenance = Maintenance.query.filter_by(id=maintenance_id).first()
        return maintenance

    @staticmethod
    def list_orders_by_id(maintenance_id):
        """
        List all orders belonging to a maintenance with given id.
        :param maintenance_id: id of the maintenance.
        :return: list of maintenance orders.
        """

        orders = Order.query.filter_by(id=maintenance_id).all()
        return orders

    @staticmethod
    def list_components_by_id(order_id):
        """
        List all components belonging to an order with given id.
        :param order_id: id of the order.
        :return: list of order components.
        """

        components = Component.query.filter_by(id=order_id).all()
        return components

    @staticmethod
    def get_vehicle_by_id(vehicle_id):
        """
        Get vehicle by id.
        :param vehicle_id: id of the vehicle.
        :return: vehicle instance.
        """

        vehicle = Vehicle.query.filter_by(vehicle_id=vehicle_id).first()
        return vehicle

    @staticmethod
    def add_maintenance(model: str, plate: str, date):
        """
        Add maintenance information to database.
        :param model: Model of the car.
        :param plate: Plate of the car.
        :param date: Date of the maintenance.
        :return: status message of operation.
        """

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
        existing_maintenance = Maintenance.query.filter_by(vehicle_id=vehicle.vehicle_id, end_date=None).all()
        if existing_maintenance:
            return (f"Maintenance for this car is already planned on"
                    f" {str(existing_maintenance[0].start_date)} and was not finished")

        maintenance = Maintenance()
        if date:
            maintenance.start_date = date
        maintenance.vehicle_id = vehicle.vehicle_id
        db.session.add(maintenance)
        db.session.commit()

        order = Order()
        order.maintenance_id = maintenance.id
        order.status = "awaiting order"

        db.session.add(order)
        db.session.commit()

        return "Successfully added maintenance."

    @staticmethod
    def delete_maintenance(maintenance_id):
        maintenance = Maintenance.query.filter_by(id=maintenance_id).first()
        if maintenance:
            db.session.delete(maintenance)
            db.session.commit()

    @staticmethod
    def update_description(maintenance_id, description, problem, start_date, end_date, status):
        maintenance = Maintenance.query.filter_by(id=maintenance_id).first()
        vehicle = Vehicle.query.filter_by(vehicle_id=maintenance.vehicle_id).first()
        maintenances_vehicles = Maintenance.query.filter_by(vehicle_id=maintenance.vehicle_id, end_date=None).all()

        if not maintenance:
            return "Maintenance does not exist."

        if not end_date and (len(maintenances_vehicles) > 0 and maintenance.end_date or len(maintenances_vehicles) > 1):
            return "Can't have at the same two ongoing maintenances."


        if end_date and status == "Maintenance":
            return "Impossible that maintenance has end date, but car didn't finish it"
        if not start_date:
            return "Can't change start date to None"
        if end_date:
            if end_date < str(maintenance.start_date):
                return "Can't set end date earlier than start date."
            maintenance.end_date = end_date
        else:
            maintenance.end_date = None

        maintenance.maintenance_description = description
        maintenance.reported_problem = problem
        maintenance.start_date = start_date

        vehicle.status = status
        db.session.commit()

        return "Successfully updated maintenance"

    @staticmethod
    def get_awaiting_order_components(maintenance_id):
        order = Order.query.filter_by(maintenance_id=maintenance_id, status="awaiting order").first()
        return order.components

    @staticmethod
    def get_awaiting_order(maintenance_id):
        order = Order.query.filter_by(maintenance_id=maintenance_id, status="awaiting order").first()
        return order

    @staticmethod
    def get_processing_orders(maintenance_id):
        orders = Order.query.filter_by(maintenance_id=maintenance_id).all()
        return [order for order in orders if order.status != "awaiting order"]

    @staticmethod
    def add_empty_need_order_row(order_id):
        component = Component()
        component.order_id = order_id
        component.name = "None"
        component.quantity = 1
        component.price = 0
        db.session.add(component)
        db.session.commit()

    @staticmethod
    def delete_component(component_id):
        component = Component.query.filter_by(id=component_id).first()
        if component:
            db.session.delete(component)
            db.session.commit()

    @staticmethod
    def save_components(components):
        for component_id in components:
            component = Component.query.filter_by(id=int(component_id)).first()
            if component:
                if components[component_id][0]:
                    component.name = components[component_id][0]
                if components[component_id][1]:
                    component.quantity = int(components[component_id][1])
                db.session.commit()
