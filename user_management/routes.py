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
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already exists')
            return redirect(url_for('user.register'))  # use 'user' as the blueprint name

        user = User(email=email)
        user.set_password(password)#already encrypted
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('user.login'))
    return render_template('register.html')


@user_management_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and not user.is_banned:
            session['user_id'] = user.id
            session['role'] = user.role
            flash('Login successful!')
            return redirect(url_for('user.profile'))
        flash('Invalid credentials or banned account.')
    return render_template('login.html')


@user_management_bp.route('/profile')
def profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('user.login'))
    user = User.query.get(user_id)
    return render_template('profile.html', user=user)


@user_management_bp.route('/delete_profile', methods=['POST'])
def delete_profile():
    user_id = session.get('user_id')
    if user_id:
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        session.clear()
        flash('Profile deleted successfully')
    return redirect(url_for('user.login'))
