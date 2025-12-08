from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

class PasswordChangeForm(FlaskForm):
    current_password = PasswordField(
        "Current Password",
        validators=[DataRequired(message="Enter your current password.")]
    )

    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(message="Enter a new password."),
            Length(min=6, message="Password must be at least 6 characters.")
        ]
    )

    confirm_new_password = PasswordField(
        "Confirm New Password",
        validators=[
            DataRequired(message="Please confirm your new password."),
            EqualTo("new_password", message="Passwords do not match.")
        ]
    )

    submit = SubmitField("Change Password")
