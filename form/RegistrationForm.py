from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[Optional(), Length(max=120)])
    surname = StringField('Surname', validators=[Optional(), Length(max=120)])
    birthdate = DateField('Birthdate', format='%Y-%m-%d', validators=[Optional()])

    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )

    submit = SubmitField('Register')
