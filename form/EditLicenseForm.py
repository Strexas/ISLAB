from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired, Length, Optional


class EditLicenseForm(FlaskForm):
    driver_license = StringField(
        'Driver License Number',
        validators=[DataRequired(), Length(min=4, max=50)]
    )
    license_expiration = DateField(
        'License Expiration Date',
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    submit = SubmitField('Update license')
