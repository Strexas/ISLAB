""" Routing rules for maintenance subsystem """

from flask import (render_template, Blueprint, request,
                   redirect, session, flash, url_for)

from .maintenance_controller import MaintenanceController

secret_key = "secret_key"

ADMIN_ROLES = ["employee", "accountant"]
maintenance_bp = Blueprint('maintenance_subsystem', __name__)


@maintenance_bp.route('/maintenances_list', methods=["GET", "POST"])
def route_maintenances_list():
    """
    Lists maintenances. Filters and adds new maintenances.
    :return: List of maintenances page.
    :return: List of maintenancsces page.
    """

    if session.get("role") not in ADMIN_ROLES:
        flash("Access denied.", "danger")
        return redirect(url_for("user_management.profile"))

    controller = MaintenanceController()

    message = ''
    plate = ''
    model = ''
    date = ''
    if request.method == "POST":
        form = request.form
        if form['button'] == "filter":
            plate = form['plate']
            model = form['model']
            date = form['date']
        elif form['button'] == "add":
            message = controller.add_maintenance(model=form['model'],
                                                 plate=form['plate'],
                                                 date=form['date'])
        elif form['button'] == "reset":
            pass
        else:
            message = "Error: Not Implemented"

    maintenances = controller.list_maintenances()
    table_view = []
    for maintenance in maintenances:
        vehicle = controller.get_vehicle_by_id(maintenance.vehicle_id)
        if (plate in vehicle.license_plate and
                model in vehicle.model and
                (date == "" or date == str(maintenance.start_date))):
            table_view.append([maintenance.id,
                               vehicle.model,
                               vehicle.license_plate,
                               str(maintenance.start_date)])

    return render_template('list_maintenance.html',
                           maintenances=table_view, message=message)


@maintenance_bp.route("/maintenance_page/<int:id_maintenance>", methods=["GET", "POST"])
def route_maintenance(id_maintenance):
    """
    Displays maintenance page, process editing.

    :param id_maintenance: id of the maintenance.
    :return: Maintenance information page.
    """

    if session.get("role") not in ADMIN_ROLES:
        flash("Access denied.", "danger")
        return redirect(url_for("user_management.profile"))

    controller = MaintenanceController()
    message = ''
    scroll = False
    if request.method == "POST":
        form = request.form
        if "button" in form:
            if form['button'] == "delete":
                controller.delete_maintenance(id_maintenance)
                return redirect('/maintenances_list')
            elif form['button'] == "save_description":
                message = controller.update_description(maintenance_id=id_maintenance,
                                                         description=form['description'],
                                                         problem=form['problem'],
                                                         start_date=form['start_date'],
                                                         end_date=form['end_date'],
                                                         status=form['status'])
            elif form['button'] == "save_need":
                components = {}
                for ids in form.keys():
                    if ids == 'button':
                        continue
                    components[ids] = form.getlist(ids)
                controller.save_components(components)
                scroll = True
            elif form['button'] == "add_need":
                controller.add_empty_need_order_row(controller.get_awaiting_order(id_maintenance).id)
                scroll = True
            elif form['button'] == "place_order":
                if session.get("role") == "accountant":
                    controller.place_order(id_maintenance)
                else:
                    flash("You are not allowed to place orders.", "danger")
                    redirect(url_for("user_management.profile"))
            elif form['button'] == "received_button":
                controller.receive_order(form["order_id"])
        elif 'delete_component' in form:
            controller.delete_component(form['delete_component'])
            scroll = True
        else:
            message = "Error: Not Implemented"

    maintenance = controller.get_maintenance_by_id(id_maintenance)
    vehicle = controller.get_vehicle_by_id(maintenance.vehicle_id)
    awaiting_order_details = controller.get_awaiting_order_components(maintenance.id)
    orders = controller.get_processing_orders(maintenance.id)
    components = {order.id: controller.get_components(order.id) for order in orders}
    total_orders = {}
    for order in components:
        total_orders[order] = 0
        for component in components[order]:
            total_orders[order] += component.quantity * component.price

    total_cost = 0
    for cost in total_orders:
        total_cost += total_orders[cost]

    return render_template('maintenance_page.html',
                           vehicle=vehicle,
                           maintenance=maintenance,
                           message=message,
                           awaiting_order_details=awaiting_order_details,
                           scroll=str(scroll).lower(),
                           orders=orders,
                           components=components,
                           total_cost=total_cost,
                           total_orders=total_orders)

@maintenance_bp.route("/maintenance/get_pending", methods=["GET"])
def get_pending():
    body = request.json
    if body["secret_key"] != secret_key:
        return {"error": "Invalid Secret Key"}
    controller = MaintenanceController()
    orders = controller.get_pending_orders()
    if not orders:
        return {}

    order = orders[0]
    return_orders = {order.id: {}}

    for component in controller.get_components(order.id):
        return_orders[order.id][component.id] = {}
        return_orders[order.id][component.id]["quantity"] = component.quantity
        return_orders[order.id][component.id]["name"] = component.name
        return_orders[order.id][component.id]["price"] = component.price

    return return_orders

@maintenance_bp.route("/maintenance/ship", methods=["POST"])
def ship():
    controller = MaintenanceController()
    body = request.json
    if body["secret_key"] != secret_key:
        return {"error": "Invalid Secret Key"}

    controller.ship_parts(body)

    return {"success": True}
