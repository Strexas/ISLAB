import os
from flask import Flask
from flask_migrate import Migrate
from context import db, mail

# Import blueprints
from subsystems.fleet_management.routes import fleet_bp
# Import other blueprints as needed...

app = Flask(__name__)

# ... (your existing configuration)

# Register blueprints
app.register_blueprint(fleet_bp)
# Register other blueprints...

if __name__ == '__main__':
    app.run(debug=True)
    
from . import routes
