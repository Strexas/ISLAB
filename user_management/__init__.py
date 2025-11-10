from flask import Blueprint

#create a bluprient for our user management
user_management_bp = Blueprint('user_management', __name__)
#import routes to register the routes with the blueprint
from . import routes