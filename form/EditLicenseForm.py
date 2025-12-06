from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class EditLicenseForm(FlaskForm):

    driver_license = StringField(
        'Driver License Number',
        validators=[DataRequired(), Length(min=5)]
    )

    submit = SubmitField('Update License')
