from flask import (render_template, request,
                   redirect, url_for, flash,
                   session, Blueprint)

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


user_management_bp = Blueprint('user_management', __name__)

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    driver_license = db.Column(db.String(50))
    role = db.Column(db.String(20), default='customer')  # customer, employee, accountant
    is_banned = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@user_management_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    #Validate the data when submitted
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please log in!')
        return redirect(url_for('user_management.login'))

    return render_template('register.html', form=form)


@user_management_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and not user.is_banned:
            session['user_id'] = user.id
            session['role'] = user.role
            flash(f'Welcome, {user.email}!')

            #Redirect depending on user role
            if user.role == 'employee' or user.role == 'accountant':
                return redirect(url_for('main.admin_dashboard'))
            return redirect(url_for('user_management.index'))

        flash('Invalid credentials or inactive/blocked account.', 'danger')

    return render_template('login.html', form=form)

@user_management_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('user_management.login'))


@user_management_bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('You need to log in to view your profile.', 'warning')
        return redirect(url_for('user_management.login'))

    user = User.query.get_or_404(user_id)
    delete_form = DeleteProfileForm()

    return render_template('profile.html', user=user, delete_form=delete_form)

@user_management_bp.route('/delete_profile', methods=['POST'])
def delete_profile():
    user_id = session.get('user_id')
    if not user_id:
        flash('Session error.', 'danger')
        return redirect(url_for('user_management.login'))

    user = User.query.get_or_404(user_id)

    form = DeleteProfileForm()
    if form.validate_on_submit() and user.check_password(form.current_password.data):
        db.session.delete(user)
        db.session.commit()
        session.clear()
        flash('Your profile has been permanently deleted.', 'success')
        return redirect(url_for('user_management.login'))

    flash('Incorrect password. Profile could not be deleted.', 'danger')
    return redirect(url_for('user_management.profile'))

@user_management_bp.route('/list_users')
def list_users():
    role = session.get('role')

    if role not in ['employee', 'accountant']:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('user_management.profile'))

    users = User.query.all()
    return render_template('list_users.html', users=users)

@user_management_bp.route('/ban_user/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    role = session.get('role')

    if role != 'employee':
        flash("Access denied.", "danger")
        return redirect(url_for('user_management.list_users'))

    user = User.query.get_or_404(user_id)
    user.is_banned = True
    db.session.commit()

    flash(f"User {user.email} has been banned.", "success")
    return redirect(url_for('user_management.list_users'))

@user_management_bp.route('/edit_license', methods=['GET', 'POST'])
def edit_license():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user_management.login'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        new_license = request.form.get('driver_license')
        user.driver_license = new_license
        db.session.commit()
        flash("Driver license updated!", "success")
        return redirect(url_for('user_management.profile'))

    return render_template('edit_license.html', user=user)

@user_management_bp.route('/index')
def index():
    return render_template('index.html')
