from flask import Blueprint, flash, redirect, render_template, request, session, url_for, jsonify

# EKLEME: Veritabanı işlemleri için gerekli
from context import db

from subsystems.reservation_subsystem.reservation_subsystem import ReservationSubsystem
from models.Vehicle import Vehicle
from models.User import User
from models.Reservation import Reservation
from models.InsurancePolicy import InsurancePolicy

reservation_blueprint = Blueprint("reservations", __name__)
reservation_subsystem = ReservationSubsystem()

@reservation_blueprint.route("/", methods=["GET"])
def index():
    return render_template("index.html", logged_in=('user_id' in session))

# ===================== RESERVE A CAR ============================
@reservation_blueprint.route("/reservations/reserve/<int:vehicle_id>", methods=["GET", "POST"])
def reserve(vehicle_id):
    # User must be logged in to reserve a vehicle
    if 'user_id' not in session:
        flash("You must be logged in to reserve a vehicle.", "error")
        return redirect(url_for("user_management.login"))

    # Fetch user details
    user = User.query.get(session['user_id'])

    # Fetch vehicle details
    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # If form submitted, process reservation
    if request.method == "POST":
        try:
            # Create initial reservation
            reservation = reservation_subsystem.create_reservation(
                user=user,
                vehicle=vehicle,
                pickup_date_s=request.form.get("pickup_date"),
                return_date_s=request.form.get("return_date")
            )

            # --- EKLEME: VERİTABANINA ZORLA KAYIT (COMMIT) ---
            # Payment sayfasına gitmeden önce ID'nin oluşması için kayıt şart.
            db.session.add(reservation)
            db.session.commit()
            # -------------------------------------------------

            
                
                
            # Sigorta seçilmese bile akışın bozulmaması için insurance sayfasına (skip için) yönlendiriyoruz
            # Veya direkt payment'a gidecekse bile ID'nin DB'de olduğundan artık eminiz.
            return redirect(url_for("reservations.add_insurance", reservation=reservation))
            
        except Exception as ex:
            db.session.rollback() # Hata durumunda geri al
            flash(ex, "error")
            return render_template("car_reserve.html", logged_in=('user_id' in session), vehicle=vehicle, user=user)



    #Get dates from index search
    pickup_date_str = request.args.get("pickup_date")
    dropoff_date_str = request.args.get("dropoff_date")

    try:
        if pickup_date_str and pickup_date_str != "" and dropoff_date_str and dropoff_date_str != "":
            pickup_date, dropoff_date = reservation_subsystem.parse_dates(pickup_date_str, dropoff_date_str)
            return render_template("car_reserve.html", logged_in=('user_id' in session), vehicle=vehicle, user=user, pickup_date=pickup_date, dropoff_date=dropoff_date)
    except Exception as e:
        flash(e, "error")

    return render_template("car_reserve.html", logged_in=('user_id' in session), vehicle=vehicle, user=user)

# ===================== RESERVATION SUCCESSFUL PAGE ============================
@reservation_blueprint.route("/reservations/success/<string:reservation_id>", methods=["GET"])
def reservation_success(reservation_id):
    # User must be logged to view reservation success
    if 'user_id' not in session:
        flash("You must be logged in to reserve a vehicle.", "error")
        return redirect(url_for("user_management.login"))


    #Fetch reservation details
    reservation = Reservation.query.get_or_404(reservation_id)
    insurnace_policy = InsurancePolicy.query.filter_by(reservation_id=reservation_id).first()
    vehicle = Vehicle.query.get_or_404(reservation.vehicle_id)
    user = User.query.get(session['user_id'])

    return render_template("reservation_success.html", vehicle=vehicle, user=user, reservation=reservation, insurance_policy=insurnace_policy)
    
# ===================== LIST ALL RESERVATIONS ============================
@reservation_blueprint.route("/reservations/list")
def list_reservations():
    #Check if user is logged
    if 'user_id' not in session:
        flash("You must be logged to access my reservations.", "error")
        return redirect(url_for("user_management.login"))
    
    reservations = Reservation.query.filter(
        Reservation.user_id == session['user_id']
    ).all();

    return render_template("reservation_list.html", reservations=reservations); 

# ===================== LIST ALL RESERVATIONS FOR ADMIN =====================
@reservation_blueprint.route("/reservations/reservationadmin")
def reservation_admin():
    #Check if user is logged
    if 'user_id' not in session:
        flash("You must be logged to access my reservations.", "error")
        return redirect(url_for("user_management.login"))
    
    # Fetch user details
    user = User.query.get(session['user_id'])
    #CHeck if the user is an admin 
    if user.role == "customer":
        flash("You must be admin to access this feture", "error")

    #Get all reservations and render
    reservations = Reservation.query.all()
    return render_template("list_reservation_admin.html", reservations=reservations);
    

# ===================== EDIT A RESERVATION ============================
@reservation_blueprint.route("/reservations/edit/<int:reservation_id>", methods=["PUT"])
def edit_reservation(reservation_id: int):
    #Check if user is logged
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    data = request.get_json()
    pickup_date_s = data.get("pickup_date")
    return_date_s = data.get("return_date")

    if not pickup_date_s or not return_date_s:
        return jsonify({"ok": False, "error": "pickup_date and return_date are required"}), 400

    try:
        return reservation_subsystem.edit_reservation(user_id, reservation_id, pickup_date_s, return_date_s)
    except Exception as ex:
        return jsonify({"ok": False, "error": ex.__str__()}), 500

# ===================== DELETE A RESERVATION ============================
@reservation_blueprint.route("/reservations/delete/<int:reservation_id>", methods=["DELETE"])
def delete_reservation(reservation_id: int):
    # Must be logged in
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    try:
        return reservation_subsystem.deletereservation(user_id, reservation_id=reservation_id)
    except Exception as ex:
        return jsonify({"ok": False, "error": ex.__str__()}), 500
    
@reservation_blueprint.route("/reservations/reserve/addinsurance", methods=["GET"])
def add_insurance():
    # --- EKLEME: URL'den gelen veriyi alıp template'e gönderiyoruz ---
    reservation_data = request.args.get("reservation")
    
    # Veri gelmediyse güvenli şekilde ana sayfaya at
    if not reservation_data:
        flash("Reservation data missing.", "error")
        return redirect(url_for("reservations.index"))

    return render_template("insurance.html", reservation=reservation_data)