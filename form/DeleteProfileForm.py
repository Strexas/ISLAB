from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired

class DeleteProfileForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    submit = SubmitField('Delete account')
