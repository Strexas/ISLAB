from flask_wtf import FlaskForm
from wtforms import (
    StringField, IntegerField, FloatField, SelectField,
    DateField, TextAreaField, BooleanField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from datetime import datetime

# ----------------------
# VEHICLE FORM
# ----------------------
class VehicleForm(FlaskForm):
    vehicle_id = StringField('Vehicle ID', validators=[DataRequired(), Length(max=50)])
    license_plate = StringField('License Plate', validators=[DataRequired(), Length(max=20)])
    manufacturer = StringField('Manufacturer', validators=[DataRequired(), Length(max=50)])
    model = StringField('Model', validators=[DataRequired(), Length(max=50)])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1950, max=datetime.now().year)])

    transmission = SelectField('Transmission', choices=[
        ('Manual', 'Manual'),
        ('Automatic', 'Automatic'),
        ('Hybrid', 'Hybrid'),
    ], validators=[DataRequired()])

    seat = IntegerField('Seats', validators=[DataRequired(), NumberRange(min=1, max=12)])

    fuel_type = SelectField('Fuel Type', choices=[
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ], validators=[DataRequired()])

    type = SelectField('Vehicle Type', choices=[
        ('Economy', 'Economy'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Van', 'Van'),
        ('Luxury', 'Luxury'),
    ], validators=[DataRequired()])

    status = SelectField('Status', choices=[
        ('Available', 'Available'),
        ('Rented', 'Rented'),
        ('Maintenance', 'Maintenance'),
        ('Inactive', 'Inactive'),
    ], validators=[DataRequired()])

    price_per_day = FloatField('Price Per Day (€)', validators=[DataRequired(), NumberRange(min=0)])

    image_url = StringField('Image URL', validators=[Optional(), Length(max=500)])
    description = TextAreaField('Description', validators=[Optional()])


# ----------------------
# RENT PRICE FORM
# ----------------------
class RentPriceForm(FlaskForm):
    price = FloatField('New Price (€)', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Effective Date', validators=[DataRequired()], default=datetime.utcnow)


# ----------------------
# REVIEW CACHE FORM
# ----------------------
class ReviewCacheForm(FlaskForm):
    average_rating = FloatField('Average Rating', validators=[Optional(), NumberRange(min=0, max=5)])
    review_count = IntegerField('Review Count', validators=[Optional(), NumberRange(min=0)])
    last_updated = DateField('Last Updated', validators=[DataRequired()], default=datetime.utcnow)
    source = StringField('Source', validators=[Optional(), Length(max=100)])


# ----------------------
# FILTER FORM
# ----------------------
class VehicleFilterForm(FlaskForm):
    type = SelectField('Vehicle Type', choices=[
        ('', 'All Types'),
        ('Economy', 'Economy'),
        ('Sedan', 'Sedan'),
        ('SUV', 'SUV'),
        ('Van', 'Van'),
        ('Luxury', 'Luxury'),
    ], validators=[Optional()])

    min_seats = IntegerField('Min Seats', validators=[Optional(), NumberRange(min=1)])
    max_price = FloatField('Max Price (€)', validators=[Optional(), NumberRange(min=0)])

    fuel_type = SelectField('Fuel Type', choices=[
        ('', 'All'),
        ('Petrol', 'Petrol'),
        ('Diesel', 'Diesel'),
        ('Electric', 'Electric'),
        ('Hybrid', 'Hybrid'),
    ], validators=[Optional()])

    status = SelectField('Status', choices=[
        ('', 'All'),
        ('Available', 'Available'),
        ('Rented', 'Rented'),
        ('Maintenance', 'Maintenance'),
        ('Inactive', 'Inactive'),
    ], validators=[Optional()])


# ----------------------
# RETIRE VEHICLE FORM
# ----------------------
class RetireVehicleForm(FlaskForm):
    reason = TextAreaField('Reason', validators=[DataRequired(), Length(min=5, max=500)])
    confirm = BooleanField('Confirm', validators=[DataRequired()])
