from flask import Flask
from config import Config
from models import db
from user_management import user_management_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# connect the blueprint to the main app
app.register_blueprint(user_management_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)



