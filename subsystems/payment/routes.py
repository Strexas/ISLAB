from flask import Blueprint, request, jsonify
from context import db
from models.Payment import Payment
from models.CreditCard import CreditCard
from models.User import User

payment_blueprint = Blueprint("payment", __name__, url_prefix="/payment")



# -----------------------------------------------------
# 1. Add money to balance
@payment_blueprint.route("/add_money", methods=["POST"])
def add_money():
    data = request.json

    user_id = data.get("user_id")
    amount = data.get("amount")

    if not user_id or not amount:
        return jsonify({"error": "Missing required fields"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.walletbalance += amount
    db.session.commit()

    return jsonify({"message": "Balance updated", "new_balance": user.walletbalance}), 200


# 2. Add bank card

@payment_blueprint.route("/add_bank_card", methods=["POST"])
def add_bank_card():
    data = request.json
    user_id = data.get("user_id")
    card_number = data.get("card_number")
    holder_name = data.get("holder_name")
    expire_date = data.get("expire_date")
    billing_address = data.get("billing_address")

    if not all([user_id, card_number, holder_name, expire_date, billing_address]):
        return jsonify({"error": "Missing required fields"}), 400

    new_card = CreditCard(
        userid=user_id,
        cardnumber=card_number,
        cardholdername=holder_name,
        expiredate=expire_date,
        billingaddress=billing_address
    )

    db.session.add(new_card)
    db.session.commit()

    return jsonify({"message": "Card added successfully"}), 201


# 3. Delete bank card

@payment_blueprint.route("/delete_bank_card/<int:card_id>", methods=["DELETE"])
def delete_bank_card(card_id):
    card = CreditCard.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found"}), 404

    db.session.delete(card)
    db.session.commit()

    return jsonify({"message": "Card deleted"}), 200


# 4. Pay from balance

@payment_blueprint.route("/pay_from_balance", methods=["POST"])
def pay_from_balance():
    data = request.json

    user_id = data.get("user_id")
    amount = data.get("amount")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.walletbalance < amount:
        return jsonify({"error": "Not enough balance"}), 400

    user.walletbalance -= amount
    db.session.commit()

    return jsonify({"message": "Payment successful", "remaining_balance": user.walletbalance}), 200


# 5. Check payment history

@payment_blueprint.route("/history/<int:user_id>", methods=["GET"])
def payment_history(user_id):
    history = Payment.query.filter_by(userid=user_id).all()

    result = [{
        "paymentid": p.paymentid,
        "date": p.date,
        "amount": p.amount,
        "status": p.status,
        "paymentmethod": p.paymentmethod,
        "description": p.description
    } for p in history]

    return jsonify(result), 200
# -----------------------------------------------------
