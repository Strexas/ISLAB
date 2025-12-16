import re
from datetime import datetime
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    session
)

from context import db
from models.Payment import Payment, PaymentStatus
from models.CreditCard import CreditCard
from models.User import User
from models.Reservation import Reservation, ReservationStatus
from models.InsurancePolicy import InsurancePolicy

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")

# -----------------------------------------------------
#  HELPER: ID EXTRACTION
# -----------------------------------------------------
def extract_id(raw_val):
    """ 
    Extracts only the numerical ID (e.g., 1) from a string 
    like '<Reservation 1>' or 'RES-2025-001'.
    """
    if not raw_val: return None
    if isinstance(raw_val, int): return raw_val
    
    s_val = str(raw_val)
    match = re.search(r'(\d+)', s_val)
    
    if match:
        return int(match.group(1))
    return None

# -----------------------------------------------------
#  INTERMEDIATE ROUTE: Confirm Insurance
# -----------------------------------------------------
@payment_bp.route("/confirm_insurance", methods=["POST"])
def confirm_insurance():
    # 1. Get data from form
    raw_res_input = request.form.get("reservation_input")
    insurance_type = request.form.get("insurance_type")
    
    # 2. Clean ID
    reservation_id = extract_id(raw_res_input)

    if not reservation_id:
        flash("Could not read reservation info. Please try again.", "danger")
        return redirect("/")

    # 3. Write to Session (to be used in payment page)
    session['checkout_reservation_id'] = reservation_id
    session['checkout_insurance_type'] = insurance_type

    # 4. Redirect to Payment Page
    return redirect(url_for('payment.payment_page', reservation_id=reservation_id))


# -----------------------------------------------------
#  GET /payment (PAYMENT PAGE)
# -----------------------------------------------------
@payment_bp.route("/", methods=["GET"])
def payment_page():
    # 1. Find ID (from URL or Session)
    raw_res_id = request.args.get('reservation_id') or session.get('checkout_reservation_id')
    reservation_id = extract_id(raw_res_id)
    
    if not reservation_id:
        flash("Reservation for payment not found.", "warning")
        return redirect("/")

    # 2. Fetch from DB
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        flash("Reservation not found in database.", "danger")
        return redirect("/")

    # 3. User and Cards (Demo: ID 1)
    user_id = session.get('user_id', 1) 
    user = User.query.get(user_id)
    cards = CreditCard.query.filter_by(userid=user_id).all()

    # 4. Calculate Price (Dynamic)
    vehicle_cost = reservation.total_amount if reservation.total_amount else 0.0
    insurance_cost = 0.0
    insurance_type = session.get('checkout_insurance_type', 'none')
    
    if insurance_type == 'standard':
        days = (reservation.return_date - reservation.pickup_date).days
        if days < 1: days = 1
        insurance_cost = days * 15.0

    total_amount = vehicle_cost + insurance_cost
    
    payments = Payment.query.filter_by(userid=user_id).order_by(Payment.date.desc()).all()

    return render_template(
        "payment.html",
        user=user,
        wallet_balance=(user.wallet_balance or 0.0),
        cards=cards,
        payments=payments,
        reservation=reservation,
        total_amount=total_amount,
        insurance_cost=insurance_cost,
        display_res_id=f"RES-2025-{reservation.reservation_id:03d}"
    )


# -----------------------------------------------------
#  POST /payment/pay_from_balance (PAYMENT PROCESS)
# -----------------------------------------------------
@payment_bp.route("/pay_from_balance", methods=["POST"])
def pay_from_balance():
    data = request.get_json() if request.is_json else request.form
    
    user_id = data.get("user_id", type=int)
    amount = data.get("amount", type=float)
    raw_res_id = data.get("reservation_id")
    description = data.get("description")

    # Clean ID
    reservation_id = extract_id(raw_res_id)

    if not user_id or amount is None:
        return jsonify({"success": False, "message": "Missing data."}), 400

    user = User.query.get(user_id)
    reservation = Reservation.query.get(reservation_id)

    if not user or not reservation:
        return jsonify({"success": False, "message": "User or Reservation not found."}), 404

    if (user.wallet_balance or 0.0) < amount:
        return jsonify({"success": False, "message": f"Insufficient Balance! (Required: €{amount})"}), 400

    try:
        # 1. Deduct from balance
        user.wallet_balance -= amount

        # 2. Payment Record
        payment = Payment(
            userid=user_id,
            reservationid=reservation_id,
            amount=amount,
            status=PaymentStatus.SUCCESS,
            paymentmethod="Balance",
            description=description,
            date=datetime.utcnow()
        )
        db.session.add(payment)

        # 3. Confirm Reservation
        reservation.status = ReservationStatus.ACTIVE
        
        # 4. Insurance Record (If exists)
        if session.get('checkout_insurance_type') == 'standard':
            days = (reservation.return_date - reservation.pickup_date).days
            if days < 1: days = 1
            ins_cost = days * 15.0
            
            policy = InsurancePolicy(
                reservation_id=reservation_id,
                provider="Bolt Standard",
                payment_amount=ins_cost,
                start_date=reservation.pickup_date,
                end_date=reservation.return_date,
                policy_number=f"POL-{reservation_id}-{int(datetime.utcnow().timestamp())}"
            )
            db.session.add(policy)

        db.session.commit()
        
        # Cleanup
        session.pop('checkout_reservation_id', None)
        session.pop('checkout_insurance_type', None)

        return jsonify({"success": True, "message": "Payment Successful!"})

    except Exception as e:
        db.session.rollback()
        print(f"ERROR: {e}")
        return jsonify({"success": False, "message": f"System error: {str(e)}"}), 500

# --- Other Functions (Same as before) ---
@payment_bp.route("/add_money", methods=["POST"])
def add_money():
    user_id = request.form.get("user_id", type=int)
    amount = request.form.get("amount", type=float)
    if user_id and amount > 0:
        user = User.query.get(user_id)
        user.wallet_balance = (user.wallet_balance or 0) + amount
        p = Payment(userid=user_id, amount=amount, status=PaymentStatus.SUCCESS, paymentmethod="Top-up", description="Wallet Load", date=datetime.utcnow())
        db.session.add(p)
        db.session.commit()
        flash("Balance topped up.", "success")
    return redirect(request.referrer or url_for('payment.payment_page'))

@payment_bp.route("/add_bank_card", methods=["POST"])
def add_bank_card():
    user_id = request.form.get("user_id", type=int)
    card = CreditCard(
        userid=user_id,
        cardholdername=request.form.get("cardholder_name"),
        cardnumber=request.form.get("card_number"),
        expiredate=request.form.get("expire_date"),
        billingaddress=request.form.get("billing_address")
    )
    db.session.add(card)
    db.session.commit()
    return redirect(request.referrer or url_for('payment.payment_page'))

@payment_bp.route("/delete_bank_card/<int:card_id>", methods=["POST"])
def delete_bank_card(card_id):
    card = CreditCard.query.get(card_id)
    if card:
        db.session.delete(card)
        db.session.commit()
    return redirect(request.referrer or url_for('payment.payment_page'))