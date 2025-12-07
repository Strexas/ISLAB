from flask import (
    render_template, request, redirect, url_for,
    flash, session, Blueprint, current_app
)
from werkzeug.utils import secure_filename
import os
import requests
from datetime import datetime
from models.AccessLog import AccessLog
from form.RegistrationForm import RegistrationForm
from form.LoginForm import LoginForm
from form.DeleteProfileForm import DeleteProfileForm
from form.EditLicenseForm import EditLicenseForm

from models.User import User
from models.Token import Token
from models.AccessLog import AccessLog
from context import db, mail

from flask_mail import Message

user_management_bp = Blueprint('user_management', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# ---------- UTILS ----------

def login_required():
    if 'user_id' not in session:
        flash("You must be logged in.", "warning")
        return False
    return True


def simulate_dot_check(license_number: str):
    """
    Simula el Department Of Transport.
    A efectos de demo: licencias que empiezan por 'A' son válidas.
    """
    return license_number.upper().startswith('A')


# ---------- REGISTER + EMAIL VERIFICATION ----------

@user_management_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        # Crear usuario
        user = User.create_user(
            email=form.email.data,
            password=form.password.data,
            name=form.name.data,
            surname=form.surname.data,
            birthdate=form.birthdate.data
        )

        # Generar token de verificación
        token_value = Token.generate(user.id, type="verify_email")

        verify_url = url_for('user_management.verify_email', token=token_value, _external=True)

        msg = Message(
            subject="Verify your Car Rental account",
            sender="noreply@carrental.com",
            recipients=[user.email],
            body=f"Welcome!\n\nPlease click the following link to verify your account:\n{verify_url}"
        )
        mail.send(msg)

        flash("Account created! Check your email to verify your account.", "info")
        return redirect(url_for('user_management.login'))

    return render_template('register.html', form=form)


@user_management_bp.route('/verify/<token>')
def verify_email(token):
    t = Token.query.filter_by(token=token, type="verify_email").first()

    if not t or not t.is_valid():
        flash("Invalid or expired verification link.", "danger")
        return redirect(url_for('user_management.login'))

    user = User.get_by_id(t.user_id)
    user.is_verified = True
    db.session.commit()

    flash("Your email has been verified. You can now log in.", "success")
    return redirect(url_for('user_management.login'))


# ---------- LOGIN / LOGOUT ----------

@user_management_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = User.authenticate(email, password)

        if not user:
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        if not user.is_verified:
            flash("Please verify your email before logging in.", "warning")
            return render_template("login.html", form=form)

        if not user.account_status:
            flash("This account is banned or inactive.", "danger")
            return render_template("login.html", form=form)

        # Login OK
        session['user_id'] = user.id
        session['role'] = user.role

        flash(f"Welcome, {user.email}!", "success")

        if user.role in ['employee', 'accountant']:
            return redirect(url_for('user_management.admin_dashboard'))
        else:
            return redirect(url_for('user_management.index'))

    return render_template("login.html", form=form)


@user_management_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('user_management.login'))


# ---------- PROFILE & DELETE PROFILE ----------

@user_management_bp.route('/profile')
def profile():
    if not login_required():
        return redirect(url_for('user_management.login'))

    user = User.get_current()
    delete_form = DeleteProfileForm()
    license_form = EditLicenseForm()

    return render_template(
        'profile.html',
        user=user,
        delete_form=delete_form,
        license_form=license_form
    )


@user_management_bp.route('/delete_profile', methods=['POST'])
def delete_profile():
    if not login_required():
        return redirect(url_for('user_management.login'))

    user = User.get_current()
    form = DeleteProfileForm()

    if form.validate_on_submit() and user.verify_password(form.current_password.data):
        user.delete()
        session.clear()
        flash("Your profile has been permanently deleted.", "success")
        return redirect(url_for('user_management.login'))

    flash("Incorrect password. Profile could not be deleted.", "danger")
    return redirect(url_for('user_management.profile'))


# ---------- LIST USERS (Office Employee + Accountant) ----------

@user_management_bp.route('/list_users')
def list_users():
    role = session.get('role')

    if role not in ['employee', 'accountant']:
        flash("You don't have permission to access this page.", "danger")
        return redirect(url_for('user_management.profile'))

    # Log access (diagrama: Log access)
    log = AccessLog(
        employee_id=session['user_id'],
        action="Viewed users list"
    )
    db.session.add(log)
    db.session.commit()

    users = User.get_all()
    return render_template('list_users.html', users=users)


# ---------- BAN USER (solo Accountant) ----------

@user_management_bp.route('/ban_user/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    role = session.get('role')

    if role != 'accountant':
        flash("Access denied. Only accountants can ban users.", "danger")
        return redirect(url_for('user_management.list_users'))

    user_to_ban = User.get_by_id(user_id)
    user_to_ban.ban()

    # Revocar sesión si es el usuario actual
    if session.get('user_id') == user_to_ban.id:
        session.clear()

    flash(f"User {user_to_ban.email} has been banned.", "success")
    return redirect(url_for('user_management.list_users'))

# ---------- ADMIN DASHBOARD ----------
@user_management_bp.route('/admin_dashboard')
def admin_dashboard():
    role = session.get("role")
    if role not in ['employee', 'accountant']:
        flash("Access denied.", "danger")
        return redirect(url_for('user_management.login'))

    return render_template("admin_dashboard.html")

# ---------- UPDATE EMAIL ----------
@user_management_bp.route('/update_email', methods=['POST'])
def update_email():
    if not login_required():
        return redirect(url_for('user_management.login'))

    user = User.get_current()
    new_email = request.form.get("new_email")

    if not new_email:
        flash("Email cannot be empty.", "danger")
        return redirect(url_for('user_management.profile'))

    existing = User.query.filter_by(email=new_email).first()
    if existing and existing.id != user.id:
        flash("This email is already in use.", "danger")
        return redirect(url_for('user_management.profile'))

    user.email = new_email
    db.session.commit()

    flash("Email updated successfully!", "success")
    return redirect(url_for('user_management.profile'))

@user_management_bp.route('/index')
def index():
    return render_template('index.html')


@user_management_bp.route('/edit_license', methods=['POST'])
def edit_license():
    if not login_required():
        return redirect(url_for('user_management.login'))

    user = User.get_current()
    form = EditLicenseForm()

    if not form.validate_on_submit():
        flash("Invalid form input.", "danger")
        return redirect(url_for('user_management.profile'))

    license_number = form.driver_license.data
    expiration_date = form.license_expiration.data

    # --- 3RD PARTY REQUEST ---
    try:
        response = requests.post(
            "http://127.0.0.1:5000/external/dot/check",
            json={"license": license_number},
            timeout=3
        )
        result = response.json()

        # Registrar log del DOT
        log = AccessLog(
            employee_id=user.id,
            action=f"DOT license check: {result}",
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()

    except Exception as e:
        flash("DOT service unavailable.", "danger")
        return redirect(url_for('user_management.profile'))

    # --- RESPONSE HANDLING ---
    if result.get("status") != "valid":
        user.license_verified = False
        db.session.commit()
        flash("DOT rejected your license.", "danger")
        return redirect(url_for('user_management.profile'))

    # DOT aceptó la licencia
    user.driver_license = license_number
    user.license_expiration = expiration_date
    user.license_verified = True
    db.session.commit()

    flash("License verified successfully!", "success")
    return redirect(url_for('user_management.profile'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_management_bp.route('/upload_license_photo', methods=['POST'])
def upload_license_photo():
    if 'user_id' not in session:
        flash("You must be logged in.", "warning")
        return redirect(url_for('user_management.login'))

    user = User.get_current()

    if 'license_photo' not in request.files:
        flash("No file part.", "danger")
        return redirect(url_for('user_management.profile'))

    file = request.files['license_photo']

    if file.filename == '':
        flash("No selected file.", "danger")
        return redirect(url_for('user_management.profile'))

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)

        # GENERAR UN NOMBRE ÚNICO PARA EVITAR COLISIONES
        unique_filename = f"user_{user.id}_{filename}"

        upload_path = os.path.join(
            current_app.root_path, 'static', 'uploads', 'licenses', unique_filename
        )

        file.save(upload_path)

        # GUARDAR LA RUTA RELATIVA EN LA BD
        user.license_photo_path = f"/static/uploads/licenses/{unique_filename}"
        db.session.commit()

        flash("License photo uploaded successfully!", "success")
    else:
        flash("Invalid file type. Allowed: png, jpg, jpeg", "danger")

    return redirect(url_for('user_management.profile'))