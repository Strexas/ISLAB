from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, BooleanField,DecimalField,SubmitField    
from wtforms.validators import DataRequired, Length, NumberRange, InputRequired

class VehicleForm(FlaskForm):
    license_plate = StringField("License Plate", validators=[DataRequired(), Length(max=20)])
    manufacturer = StringField("Manufacturer", validators=[DataRequired(), Length(max=80)])
    model = StringField("Model", validators=[DataRequired(), Length(max=80)])
    year = IntegerField("Year", validators=[DataRequired(), NumberRange(min=1980, max=2100)])

    transmission = StringField("Transmission")
    seats = IntegerField("Seats", validators=[NumberRange(min=1, max=9)])
    fuel_type = StringField("Fuel Type")

    status = SelectField(
        "Status",
        choices=[
            ("Available", "Available"),
            ("Rented", "Rented"),
            ("Maintenance", "Maintenance"),
            ("Inactive", "Inactive"),
        ],
        default="Available",
    )

    current_price = DecimalField("Daily Price", places=2, validators=[DataRequired()])

    submit = SubmitField("Save")

