from flask import (
    render_template, request, redirect, url_for,
    flash, session, Blueprint
)
from form.RegistrationForm import RegistrationForm
from form.LoginForm import LoginForm
from form.DeleteProfileForm import DeleteProfileForm
from form.EditLicenseForm import EditLicenseForm
from models.User import User  
from context import db

user_management_bp = Blueprint('user_management', __name__)

# REGISTER
@user_management_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        User.create_user(
            email=form.email.data,
            password=form.password.data
        )
        flash('Registration successful. Please log in!')
        return redirect(url_for('user_management.login'))

    return render_template('register.html', form=form)

# LOGIN
@user_management_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(
            email=form.email.data,
            password=form.password.data
        )

        if user:
            session['user_id'] = user.id
            session['role'] = user.role

            flash(f"Welcome, {user.email}!")
            if user.role in ['employee', 'accountant']:
                return redirect(url_for('main.admin_dashboard'))

            return redirect(url_for('user_management.index'))

        flash('Invalid credentials or banned account.', 'danger')

    return render_template('login.html', form=form)

# LOGOUT
@user_management_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('user_management.login'))

# PROFILE
@user_management_bp.route('/profile')
def profile():
    user = User.get_current()

    if not user:
        flash('You need to log in to view your profile.', 'warning')
        return redirect(url_for('user_management.login'))

    delete_form = DeleteProfileForm()
    return render_template('profile.html', user=user, delete_form=delete_form)

# DELETE PROFILE
@user_management_bp.route('/delete_profile', methods=['POST'])
def delete_profile():
    user = User.get_current()
    if not user:
        flash("Session error.", "danger")
        return redirect(url_for('user_management.login'))

    form = DeleteProfileForm()
    if form.validate_on_submit() and user.verify_password(form.current_password.data):
        user.delete()
        session.clear()
        flash("Your profile has been permanently deleted.", "success")
        return redirect(url_for('user_management.login'))

    flash("Incorrect password. Profile could not be deleted.", "danger")
    return redirect(url_for('user_management.profile'))

# LIST USERS (employees + accountants)
@user_management_bp.route('/list_users')
def list_users():
    if session.get('role') not in ['employee', 'accountant']:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('user_management.profile'))

    users = User.get_all()
    return render_template('list_users.html', users=users)

# BAN USER (employees only)
@user_management_bp.route('/ban_user/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    if session.get('role') != 'employee':
        flash("Access denied.", "danger")
        return redirect(url_for('user_management.list_users'))

    user = User.get_by_id(user_id)
    user.ban()

    flash(f"User {user.email} has been banned.", "success")
    return redirect(url_for('user_management.list_users'))

# EDIT LICENSE
@user_management_bp.route('/edit_license', methods=['GET', 'POST'])
def edit_license():
    user = User.get_current()
    if not user:
        return redirect(url_for('user_management.login'))

    if request.method == 'POST':
        new_license = request.form.get('driver_license')
        user.update_license(new_license)
        flash("Driver license updated!", "success")
        return redirect(url_for('user_management.profile'))

    return render_template('edit_license.html', user=user)

# INDEX
@user_management_bp.route('/index')
def index():
    return render_template('index.html')
