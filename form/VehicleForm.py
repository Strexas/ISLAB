from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, TextAreaField, BooleanField,DecimalField,SubmitField    
from wtforms.validators import DataRequired, Length, NumberRange

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

class RetireVehicleForm(FlaskForm):
    reason = TextAreaField('Reason for Retirement', validators=[DataRequired(), Length(min=5, max=500)])
    confirm = BooleanField('Confirm retirement', validators=[DataRequired()])

class ReviewCacheForm(FlaskForm):
    average_rating = DecimalField(
        "Average Rating",
        validators=[NumberRange(min=0, max=5)]
    )
    review_count = IntegerField(
        "Review Count",
        validators=[NumberRange(min=0)]
    )
    source = StringField("Source", validators=[Length(max=80)])
    submit = SubmitField("Save")