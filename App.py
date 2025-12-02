from flask import Flask
from Config import Config
from Models import db
from user_management import user_management_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    app.register_blueprint(user_management_bp)

    with app.app_context():
        db.create_all()
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
