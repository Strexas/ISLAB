from flask import (
    render_template, request, redirect, url_for,
    flash, session, Blueprint, current_app
)
from form.PasswordChangeForm import PasswordChangeForm
from form.EditLicenseForm import EditLicenseForm as LicenseForm
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

        # Si un employee/accountant está loggeado → puede elegir rol
        if session.get("role") in ["employee", "accountant"]:
            selected_role = form.role.data
        else:
            selected_role = "customer"

        # Crear usuario
        user = User.create_user(
            email=form.email.data,
            password=form.password.data,
            name=form.name.data,
            surname=form.surname.data,
            birthdate=form.birthdate.data,
            role=selected_role
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

        result = User.authenticate(form.email.data, form.password.data)

        if result == "banned":
            flash("Your account has been banned. Contact support.", "danger")
            return render_template("login.html", form=form)

        if result == "disabled":
            flash("Your account has been deactivated.", "danger")
            return render_template("login.html", form=form)

        if not result:
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        user = result

        if not user.is_verified:
            flash("Please verify your email before logging in.", "info")
            return render_template("login.html", form=form)

        session["user_id"] = user.id
        session["role"] = user.role

        if user.role == "accountant":
            return redirect(url_for("user_management.list_users"))  # ADMIN PANEL

        return redirect(url_for("user_management.profile"))  # CUSTOMER AREA

    return render_template("login.html", form=form)

@user_management_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('user_management.login'))


# ---------- PROFILE & DELETE PROFILE ----------
@user_management_bp.route("/profile")
def profile():
    user = User.get_current()
    if not user:
        return redirect(url_for("user_management.login"))

    license_form = LicenseForm()
    delete_form = DeleteProfileForm()
    password_form = PasswordChangeForm()  

    return render_template(
        "profile.html",
        user=user,
        license_form=license_form,
        delete_form=delete_form,
        password_form=password_form
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

    search = request.args.get("search", "").strip()

    query = User.query

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.name.ilike(search_term),
                User.surname.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    users = query.order_by(User.id).all()

    return render_template('list_users.html', users=users, search=search)


# ---------- BAN USER (solo Accountant) ----------

@user_management_bp.route('/ban_user/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    role = session.get('role')

    if role != 'accountant':
        flash("Access denied. Only accountants can ban users.", "danger")
        return redirect(url_for('user_management.list_users'))

    user_to_ban = User.get_by_id(user_id)
    user_to_ban.ban()

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

@user_management_bp.route('/unban_user/<int:user_id>', methods=['POST'])
def unban_user(user_id):
    role = session.get('role')

    if role != 'accountant':
        flash("Access denied. Only accountants can unban users.", "danger")
        return redirect(url_for('user_management.list_users'))

    user_to_unban = User.get_by_id(user_id)
    user_to_unban.unban()

    flash(f"User {user_to_unban.email} has been unbanned.", "success")
    return redirect(url_for('user_management.list_users'))


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

        unique_filename = f"user_{user.id}_{filename}"

        upload_path = os.path.join(
            current_app.root_path, 'static', 'uploads', 'licenses', unique_filename
        )

        file.save(upload_path)

        user.license_photo_path = f"/static/uploads/licenses/{unique_filename}"
        db.session.commit()

        flash("License photo uploaded successfully!", "success")
    else:
        flash("Invalid file type. Allowed: png, jpg, jpeg", "danger")

    return redirect(url_for('user_management.profile'))

@user_management_bp.route("/create_admin", methods=["POST"])
def create_admin():
    from flask import current_app

    # Seguridad básica: solo permitir cuando el servidor está en modo debug
    if not current_app.debug:
        return {"error": "Not allowed in production"}, 403

    data = request.json or {}

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "Email and password required"}, 400

    # Comprobar si ya existe
    existing = User.query.filter_by(email=email).first()
    if existing:
        return {"error": "User already exists"}, 400

    # Crear usuario admin
    admin = User(
        email=email,
        name="System",
        surname="Admin",
        role="accountant",        # <<< Admin
        account_status=True,
        is_verified=True           # Saltamos verificación email
    )
    admin.set_password(password)

    db.session.add(admin)
    db.session.commit()

    return {"message": "Admin created successfully"}

@user_management_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    # Solo accountant puede borrar
    if session.get("role") != "accountant":
        flash("Access denied. Only accountants can delete users.", "danger")
        return redirect(url_for('user_management.list_users'))

    user = User.get_by_id(user_id)

    # Evita que un admin se elimine a sí mismo
    if user.id == session.get("user_id"):
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for('user_management.list_users'))

    # Eliminar usuario
    db.session.delete(user)
    db.session.commit()

    flash(f"User {user.email} has been permanently deleted.", "success")
    return redirect(url_for('user_management.list_users'))

@user_management_bp.route("/change_password", methods=["POST"])
def change_password():
    password_form = PasswordChangeForm()

    if password_form.validate_on_submit():
        user = User.get_current()

        if not user.verify_password(password_form.old_password.data):
            flash("Incorrect current password.", "danger")
            return redirect(url_for("user_management.profile"))

        if password_form.new_password.data != password_form.confirm_new_password.data:
            flash("New passwords do not match.", "danger")
            return redirect(url_for("user_management.profile"))

        user.set_password(password_form.new_password.data)
        db.session.commit()

        flash("Password updated successfully!", "success")
        return redirect(url_for("user_management.profile"))

    flash("Invalid input.", "danger")
    return redirect(url_for("user_management.profile"))

@user_management_bp.route("/profile/<int:user_id>")
def view_user_profile(user_id):
    role = session.get("role")

    if role not in ["employee", "accountant"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_management.profile"))

    user = User.get_by_id(user_id)

    return render_template(
        "profile.html",
        user=user,
        license_form=None,   
        delete_form=None,   
        password_form=None   
    )
