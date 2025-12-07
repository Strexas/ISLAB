from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)

from context import db
from models.Payment import Payment, PaymentStatus
from models.CreditCard import CreditCard
from models.User import User

payment_bp = Blueprint("payment", __name__, url_prefix="/payment")


# -----------------------------------------------------
#  GET /payment  
@payment_bp.route("/", methods=["GET"])
def payment_page():
    # Demo için sabit kullanıcı
    user_id = 1

    user = User.query.get(user_id)
    wallet_balance = user.wallet_balance if user and user.wallet_balance is not None else 0.0

    cards = CreditCard.query.filter_by(userid=user_id).all()

    payments = (
        Payment.query
        .filter_by(userid=user_id)
        .order_by(Payment.date.desc(), Payment.paymentid.desc())
        .all()
    )

    return render_template(
        "payment.html",
        user=user,
        wallet_balance=wallet_balance,
        cards=cards,
        payments=payments,
    )


# -----------------------------------------------------
#  POST /payment/add_bank_card
# -----------------------------------------------------
@payment_bp.route("/add_bank_card", methods=["POST"])
def add_bank_card():
    user_id = request.form.get("user_id", type=int)
    holder_name = request.form.get("cardholder_name")
    card_number = request.form.get("card_number")
    expire_date = request.form.get("expire_date")
    billing_address = request.form.get("billing_address")

    if not all([user_id, holder_name, card_number, expire_date, billing_address]):
        flash("Missing fields for bank card.", "danger")
        return redirect(url_for("payment.payment_page"))

    card = CreditCard(
        userid=user_id,
        cardholdername=holder_name,
        cardnumber=card_number,
        expiredate=expire_date,       # string : DATE, PostgreSQL parse (YYYY-MM-DD)
        billingaddress=billing_address,
    )

    db.session.add(card)
    db.session.commit()

    flash("Card added successfully.", "success")
    return redirect(url_for("payment.payment_page"))


# -----------------------------------------------------
#  POST /payment/delete_bank_card/<id>
# -----------------------------------------------------
@payment_bp.route("/delete_bank_card/<int:card_id>", methods=["POST"])
def delete_bank_card(card_id):
    card = CreditCard.query.get(card_id)
    if not card:
        flash("Card not found.", "danger")
        return redirect(url_for("payment.payment_page"))

    db.session.delete(card)
    db.session.commit()

    flash("Card deleted.", "info")
    return redirect(url_for("payment.payment_page"))


# -----------------------------------------------------
#  POST /payment/add_money                     
# -----------------------------------------------------
@payment_bp.route("/add_money", methods=["POST"])
def add_money():
    user_id = request.form.get("user_id", type=int)
    amount = request.form.get("amount", type=float)

    if not user_id or amount is None:
        flash("Missing data for top-up.", "danger")
        return redirect(url_for("payment.payment_page"))

    if amount <= 0:
        flash("Amount must be positive.", "danger")
        return redirect(url_for("payment.payment_page"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("payment.payment_page"))

    # Cüzdanı güncelle
    current = user.wallet_balance or 0.0
    user.wallet_balance = current + amount

    # Payment kaydı
    payment = Payment(
        userid=user_id,
        reservationid=None,
        amount=amount,
        status=PaymentStatus.SUCCESS,
        paymentmethod="Top-up",
        description="Wallet top-up",
        date=datetime.utcnow(),
    )

    db.session.add(payment)
    db.session.commit()

    flash("Balance updated successfully.", "success")
    return redirect(url_for("payment.payment_page"))


# -----------------------------------------------------
#  POST /payment/pay_from_balance                            
# -----------------------------------------------------
@payment_bp.route("/pay_from_balance", methods=["POST"])
def pay_from_balance():
    user_id = request.form.get("user_id", type=int)
    amount = request.form.get("amount", type=float)
    reservation_id = request.form.get("reservation_id")  # String (UUID tarzı)
    description = request.form.get("description") or "Pay reservation from wallet"

    if not user_id or amount is None:
        flash("Missing data for payment.", "danger")
        return redirect(url_for("payment.payment_page"))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for("payment.payment_page"))

    if (user.wallet_balance or 0.0) < amount:
        flash("Insufficient wallet balance.", "danger")
        return redirect(url_for("payment.payment_page"))

    # Bakiyeden düş
    user.wallet_balance = (user.wallet_balance or 0.0) - amount

    # Payment kaydı
    payment = Payment(
        userid=user_id,
        reservationid=reservation_id,
        amount=amount,
        status=PaymentStatus.SUCCESS,
        paymentmethod="Balance",
        description=description,
        date=datetime.utcnow(),
    )

    db.session.add(payment)
    db.session.commit()

    flash("Payment completed from wallet.", "success")
    return redirect(url_for("payment.payment_page"))


# -----------------------------------------------------
#  GET /payment/history/<user_id>                 
# -----------------------------------------------------
@payment_bp.route("/history/<int:user_id>", methods=["GET"])
def payment_history(user_id):
    history = (
        Payment.query
        .filter_by(userid=user_id)
        .order_by(Payment.date.desc())
        .all()
    )

    data = []
    for p in history:
        data.append({
            "paymentid": p.paymentid,
            "date": p.date.strftime("%Y-%m-%d %H:%M"),
            "amount": p.amount,
            "status": p.status.value if isinstance(p.status, PaymentStatus) else str(p.status),
            "method": p.paymentmethod,
            "description": p.description,
        })

    return jsonify(data)
