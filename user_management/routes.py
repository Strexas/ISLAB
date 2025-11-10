from flask import render_template, request, redirect, url_for, flash, session
from models import db, User
from . import user_management_bp  # import the blueprint defined in __init__.py

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
