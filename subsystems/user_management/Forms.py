from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from Models import User  


class RegistrationForm(FlaskForm):
    """Form for registering a new user"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match.')]
    )

    submit = SubmitField('Register')

    def validate_email(self, email):
        """
        Checks if the email is already registered
        :param email: string email ot validate
        :return: None. Raises ValidationError if email is already registered
        """

        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class DeleteProfileForm(FlaskForm):
    # Password field used to fulfill verification requirements
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    submit = SubmitField('Confirm Deletion')
