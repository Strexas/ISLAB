from flask import Blueprint
from models.User import User
from models.Token import Token
from models.Log import Log

user_management_bp = Blueprint('user_management', __name__)

from . import routes
