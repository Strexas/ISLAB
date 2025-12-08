from flask import render_template, Blueprint


maintenance_subsystem_blueprint = Blueprint('maitenance_subsystem', __name__)


@maintenance_subsystem_blueprint.route('/admin', methods=['GET', 'POST'])
def admin_page():
    return render_template('admin.html')


@maintenance_subsystem_blueprint.route('/list_maintenances', methods=['GET', 'POST'])
def list_maintenances_page():
    return render_template('list_maintenance.html')


@maintenance_subsystem_blueprint.route('/maintenance_page/', methods=['GET', 'POST'])
def maintenance_page():
    return render_template('maintenance_page.html')
