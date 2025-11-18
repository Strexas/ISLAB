from flask import Flask
from user_management.routes import user_management_bp as user_management_blueprint

app = Flask(__name__)

@app.route('/')
def index():
    return 'DEFAULT PAGE'

# db.init_app(app)

# connect the blueprint to the main app
app.register_blueprint(user_management_blueprint)



if __name__ == '__main__':
    # with app.app_context():
    #     db.create_all()
    app.run(debug=True)



