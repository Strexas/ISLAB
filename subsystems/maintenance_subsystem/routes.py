""" Routing rules for maintenance subsystem and admin page """

from flask import render_template, Blueprint, request, redirect

from .maintenance_controller import MaintenanceController


maintenance_bp = Blueprint('maintenance_subsystem', __name__)


@maintenance_bp.route('/admin')
def route_admin():
    """
    Renders static admin page.
    :return: Admin dashboard page.
    """

    return render_template('admin_dashboard.html')


@maintenance_bp.route('/maintenances_list', methods=["GET", "POST"])
def route_maintenances_list():
    """
    Lists maintenances. Filters and adds new maintenances.
    :return: List of maintenances page.
    """

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
            elif form['button'] == "add_need":
                controller.add_empty_need_order_row(controller.get_awaiting_order(id_maintenance).id)
                scroll = True
        elif 'delete_component' in form:
            controller.delete_component(form['delete_component'])
            scroll = True
        else:
            message = "Error: Not Implemented"
    maintenance = controller.get_maintenance_by_id(id_maintenance)
    vehicle = controller.get_vehicle_by_id(maintenance.vehicle_id)
    awaiting_order_details = controller.get_awaiting_order_components(maintenance.id)

    return render_template('maintenance_page.html',
                           vehicle=vehicle,
                           maintenance=maintenance,
                           message=message,
                           awaiting_order_details=awaiting_order_details,
                           scroll=scroll)
