from flask import Blueprint, request, jsonify
from context import db
from models.Payment import Payment, PaymentStatus
from models.CreditCard import CreditCard
from models.User import User
from datetime import datetime

payment_blueprint = Blueprint("payment", __name__, url_prefix="/payment")


# -----------------------------------------------------
# ADD MONEY TO BALANCE

@payment_blueprint.route("/add_money", methods=["POST"])
def add_money():
    user_id = request.form.get("user_id")
    amount = request.form.get("amount")

    if not user_id or not amount:
        return "Missing fields", 400

    try:
        amount = float(amount)
    except:
        return "Invalid amount", 400

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    user.walletbalance += amount

    payment = Payment(
        userid=user_id,
        reservationid=None,
        amount=amount,
        status=PaymentStatus.SUCCESS,
        paymentmethod="Top-up",
        description="Wallet top-up",
        date=datetime.utcnow()
    )

    db.session.add(payment)
    db.session.commit()

    return "Balance updated successfully."


# -----------------------------------------------------
# ADD BANK CARD

@payment_blueprint.route("/add_bank_card", methods=["POST"])
def add_bank_card():
    user_id = request.form.get("user_id")
    holder_name = request.form.get("cardholder_name")
    card_number = request.form.get("card_number")
    expire_date = request.form.get("expire_date")
    billing_address = request.form.get("billing_address")

    if not all([user_id, holder_name, card_number, expire_date, billing_address]):
        return "Missing fields", 400

    card = CreditCard(
        userid=user_id,
        cardholdername=holder_name,
        cardnumber=card_number,
        expiredate=expire_date,
        billingaddress=billing_address
    )

    db.session.add(card)
    db.session.commit()

    return "Card added successfully"


# -----------------------------------------------------
# DELETE BANK CARD (HTML FORM → POST)

@payment_blueprint.route("/delete_bank_card/<int:card_id>", methods=["POST"])
def delete_bank_card(card_id):
    card = CreditCard.query.get(card_id)
    if not card:
        return "Card not found", 404

    db.session.delete(card)
    db.session.commit()

    return "Card deleted successfully."


# -----------------------------------------------------
# PAY FROM BALANCE 

@payment_blueprint.route("/pay_from_balance", methods=["POST"])
def pay_from_balance():
    user_id = request.form.get("user_id")
    amount = float(request.form.get("amount", 0))
    reservation_id = request.form.get("reservation_id")
    description = request.form.get("description")

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    if user.walletbalance < amount:
        return "Insufficient balance", 400

    user.walletbalance -= amount

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
    db.session.commit()

    return "Payment successful."


# -----------------------------------------------------
# PAYMENT HISTORY

@payment_blueprint.route("/history/<int:user_id>", methods=["GET"])
def payment_history(user_id):
    history = Payment.query.filter_by(userid=user_id).order_by(Payment.date.desc()).all()

    data = []
    for p in history:
        data.append({
            "paymentid": p.paymentid,
            "date": p.date.strftime("%Y-%m-%d %H:%M"),
            "amount": p.amount,
            "status": p.status.value,
            "method": p.paymentmethod,
            "description": p.description
        })

    return jsonify(data)

# -----------------------------------------------------
