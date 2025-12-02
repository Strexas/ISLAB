class Config:
    SECRET_KEY = "1234"

    SQLALCHEMY_DATABASE_URI = (
        "postgresql://postgres:Mariaajo8!@localhost/miapp"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
