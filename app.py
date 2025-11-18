from flask import Flask
from user_management.routes import user_management_bp as user_management_blueprint


app = Flask(__name__)


@app.route('/')
def index():
    return 'DEFAULT PAGE'


if __name__ == '__main__':
    app.register_blueprint(user_management_blueprint)
    app.run(debug=True)
