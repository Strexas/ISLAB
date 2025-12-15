from flask import (
    render_template, request, redirect, url_for,
    flash, session, Blueprint, current_app
)

from form.RegistrationForm import RegistrationForm
from form.LoginForm import LoginForm
from form.DeleteProfileForm import DeleteProfileForm
from form.EditLicenseForm import EditLicenseForm, EditLicenseForm as LicenseForm
from form.PasswordChangeForm import PasswordChangeForm


from models.User import User
from models.Token import Token
from models.Log import Log


from .UserManagementController import UserManagementController


from context import db, mail


from werkzeug.utils import secure_filename
from flask_mail import Message
from datetime import datetime
import os
import requests
from flask import request, jsonify
import requests
from context import db

user_management_bp = Blueprint('user_management', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


ADMIN_ROLES = ["employee", "accountant"]

def login_required():
    if 'user_id' not in session:
        flash("You must be logged in.", "warning")
        return False
    return True


# ---------- REGISTER ----------

@user_management_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():

        if session.get("role") in ["employee", "accountant"]:
            selected_role = form.role.data
        else:
            selected_role = "customer"

        user = UserManagementController.create_user(
            email=form.email.data,
            password=form.password.data,
            name=form.name.data,
            surname=form.surname.data,
            birthdate=form.birthdate.data,
            role=selected_role
        )

        token_value = UserManagementController.generate_token(user.id, type="verify_email")
        verify_url = url_for(
            'user_management.verify_email',
            token=token_value,
            _external=True
        )

        msg = Message(
            subject="Verify your Car Rental account",
            sender="noreply@carrental.com",
            recipients=[user.email],
            body=f"Welcome!\n\nVerify your account:\n{verify_url}"
        )
        mail.send(msg)

        flash("Account created! Check your email to verify your account.", "info")
        return redirect(url_for('user_management.login'))

    return render_template('register.html', form=form)


# ---------- EMAIL VERIFICATION ----------

@user_management_bp.route('/verify/<token>')
def verify_email(token):
    t = Token.query.filter_by(token=token, type="verify_email").first()

    if not t or not t.is_valid():
        flash("Invalid or expired verification link.", "danger")
        return redirect(url_for('user_management.login'))

    user = UserManagementController.get_by_id(t.user_id)
    user.is_verified = True
    db.session.commit()

    flash("Your email has been verified.", "success")
    return redirect(url_for('user_management.login'))


# ---------- LOGIN / LOGOUT ----------

@user_management_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():

        result = UserManagementController.authenticate(
            form.email.data,
            form.password.data
        )

        if result == "banned":
            flash("Your account has been banned.", "danger")
            return render_template("login.html", form=form)

        if result == "disabled":
            flash("Your account has been deactivated.", "danger")
            return render_template("login.html", form=form)

        if not result:
            flash("Invalid email or password.", "danger")
            return render_template("login.html", form=form)

        user = result

        if not user.is_verified:
            flash("Please verify your email first.", "info")
            return render_template("login.html", form=form)

        session["user_id"] = user.id
        session["role"] = user.role

        return redirect(
            url_for(
                "user_management.list_users"
                if user.role in ["accountant", "employee"]
                else "user_management.profile"
            )
        )

    return render_template("login.html", form=form)


@user_management_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for('user_management.login'))


# ---------- PROFILE ----------

@user_management_bp.route("/profile")
def profile():
    user = UserManagementController.get_current()
    if not user:
        return redirect(url_for("user_management.login"))
    db.session.refresh(user)
    return render_template(
        "profile.html",
        user=user,
        license_form=LicenseForm(),
        delete_form=DeleteProfileForm(),
        password_form=PasswordChangeForm()
    )


# ---------- DELETE OWN PROFILE ----------

@user_management_bp.route('/delete_profile', methods=['POST'])
def delete_profile():
    if not login_required():
        return redirect(url_for('user_management.login'))

    user = UserManagementController.get_current()
    form = DeleteProfileForm()

    if form.validate_on_submit() and user.verify_password(form.current_password.data):
        UserManagementController.delete(user)
        session.clear()
        flash("Profile deleted.", "success")
        return redirect(url_for('user_management.login'))

    flash("Incorrect password.", "danger")
    return redirect(url_for('user_management.profile'))


# ---------- LIST USERS ----------

@user_management_bp.route('/list_users')
def list_users():
    role = session.get('role')

    if role not in ADMIN_ROLES:
        flash("Access denied.", "danger")
        return redirect(url_for('user_management.profile'))

    search = request.args.get("search", "").strip()
    query = User.query

    if search:
        term = f"%{search}%"
        query = query.filter(
            db.or_(
                User.name.ilike(term),
                User.surname.ilike(term),
                User.email.ilike(term)
            )
        )

    users = query.order_by(User.id).all()
    return render_template('list_users.html', users=users, search=search)


# ---------- BAN / UNBAN ----------

@user_management_bp.route('/ban_user/<int:user_id>', methods=['POST'])
def ban_user(user_id):
    if session.get('role') not in ADMIN_ROLES:
        flash("Access denied.", "danger")
        return redirect(url_for('user_management.list_users'))

    user = UserManagementController.get_by_id(user_id)
    UserManagementController.ban(user)

    if session.get('user_id') == user.id:
        session.clear()

    flash(f"User {user.email} banned.", "success")
    return redirect(url_for('user_management.list_users'))


@user_management_bp.route('/unban_user/<int:user_id>', methods=['POST'])
def unban_user(user_id):
    if session.get('role') != 'accountant':
        flash("Access denied.", "danger")
        return redirect(url_for('user_management.list_users'))

    user = UserManagementController.get_by_id(user_id)
    UserManagementController.unban(user)

    flash(f"User {user.email} unbanned.", "success")
    return redirect(url_for('user_management.list_users'))


# ---------- DELETE USER (ADMIN) ----------

@user_management_bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if session.get('role') not in ADMIN_ROLES:
        flash("Access denied.", "danger")
        return redirect(url_for('user_management.list_users'))

    user = UserManagementController.get_by_id(user_id)

    if user.id == session.get("user_id"):
        flash("You cannot delete your own account.", "warning")
        return redirect(url_for('user_management.list_users'))

    UserManagementController.delete(user)
    flash(f"User {user.email} deleted.", "success")
    return redirect(url_for('user_management.list_users'))


# ---------- CHANGE PASSWORD ----------

@user_management_bp.route("/change_password", methods=["POST"])
def change_password():
    form = PasswordChangeForm()
    user = UserManagementController.get_current()

    if form.validate_on_submit():

        if not user.verify_password(form.old_password.data):
            flash("Incorrect current password.", "danger")
            return redirect(url_for("user_management.profile"))

        if form.new_password.data != form.confirm_new_password.data:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("user_management.profile"))

        user.set_password(form.new_password.data)
        db.session.commit()

        flash("Password updated.", "success")
        return redirect(url_for("user_management.profile"))

    flash("Invalid input.", "danger")
    return redirect(url_for("user_management.profile"))

@user_management_bp.route('/update_email', methods=['POST'])
def update_email():
    if not login_required():
        return redirect(url_for('user_management.login'))

    user = UserManagementController.get_current()
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

@user_management_bp.route('/edit_license', methods=['POST'])
def edit_license():
    user = UserManagementController.get_current()
    form = EditLicenseForm()

    if not form.validate_on_submit():
        flash("Invalid form input.", "danger")
        return redirect(url_for('user_management.profile'))

    license_number = form.driver_license.data
    expiration_date = form.license_expiration.data

    try:
        response = requests.post(
            "http://127.0.0.1:5000/external/dot/check",
            json={"license": license_number},
            timeout=3
        )
        result = response.json()

    except Exception:
        flash("DOT service unavailable.", "danger")
        return redirect(url_for('user_management.profile'))

    if result.get("status") != "valid":
        user.license_verified = False
        db.session.commit()
        flash("DOT rejected your license.", "danger")
        return redirect(url_for('user_management.profile'))

    user.driver_license = license_number
    user.license_expiration = expiration_date
    user.license_verified = True
    db.session.commit()

    flash("License verified successfully!", "success")
    return redirect(url_for('user_management.profile'))

@user_management_bp.route('/upload_license_photo', methods=['POST'])
def upload_license_photo():
    if not login_required():
        return redirect(url_for('user_management.login'))

    user = UserManagementController.get_current()

    if 'license_photo' not in request.files:
        flash("No file part.", "danger")
        return redirect(url_for('user_management.profile'))

    file = request.files['license_photo']

    if file.filename == '':
        flash("No selected file.", "danger")
        return redirect(url_for('user_management.profile'))

    if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename)
        unique_filename = f"user_{user.id}_{filename}"

        upload_path = os.path.join(
            current_app.root_path,
            'static',
            'uploads',
            'licenses',
            unique_filename
        )

        file.save(upload_path)

        user.license_photo_path = f"/static/uploads/licenses/{unique_filename}"
        db.session.commit()

        flash("License photo uploaded successfully!", "success")
    else:
        flash("Invalid file type. Allowed: png, jpg, jpeg", "danger")

    return redirect(url_for('user_management.profile'))

@user_management_bp.route("/profile/<int:user_id>")
def view_user_profile(user_id):
    role = session.get("role")

    if role not in ["employee", "accountant"]:
        flash("Access denied.", "danger")
        return redirect(url_for("user_management.profile"))

    user = UserManagementController.get_by_id(user_id)

    return render_template(
        "profile.html",
        user=user,
        license_form=None,
        delete_form=None,
        password_form=None
    )
