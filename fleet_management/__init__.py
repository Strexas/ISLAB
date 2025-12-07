from flask import Blueprint

fleet_bp = Blueprint("fleet_bp", __name__,
                                template_folder="../templates")

from . import routes