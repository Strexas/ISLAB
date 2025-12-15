from datetime import datetime
from models.User import User
from models.Vehicle import Vehicle
from models.Reservation import Reservation, ReservationStatus
from models.InsurancePolicy import InsurancePolicy
from models.RentPrice import RentPrice
from context import db
from flask import jsonify
import uuid

class ReservationSubsystem:
    def __init__(self):
        pass

    # ====================== CREATE RESERVATION ============================
    def create_reservation(self, user: User, vehicle: Vehicle, pickup_date_s: str, return_date_s: str) -> Reservation:
        #Parse and validate dates
        pickup_date, return_date = self.parse_dates(pickup_date_s, return_date_s)
        
        #Check availability
        if not self.is_car_available(vehicle.id, pickup_date, return_date):
            raise ValueError("The selected vehicle is not available for the chosen dates.")

        price_row = RentPrice.query.filter(RentPrice.vehicle_id == vehicle.id).first()
        daily_rate = daily_rate = price_row.price if price_row else 0

        #Calculate total amount
        days = (return_date - pickup_date).days
        # At least one day billing
        if days <= 0:
            days = 1 
        total_amount = daily_rate * days

        #Create reservation record
        reservation = Reservation(
            user_id=user.id,
            vehicle_id=vehicle.vehicle_id,
            total_amount=total_amount,
            pickup_date=pickup_date,
            return_date=return_date,
            status=ReservationStatus.PENDING
        )

        db.session.add(reservation)
        db.session.flush()
        
        return reservation

    # ========================= ATTACH INSURNACE =========================
    def add_insurance_to_reservation(self, reservation: Reservation, provider: str, amount: float) -> InsurancePolicy:
        # Create insurance policy
        policy = InsurancePolicy(
            reservation_id=reservation.reservation_id,
            provider=provider,
            payment_amount=amount,
            start_date=reservation.pickup_date,
            end_date=reservation.return_date,
            policy_number=f"POL-{str(uuid.uuid4())}"
        )

        db.session.add(policy)
        db.session.flush()

        return policy

    # ========================= FINALIZE AND SAVE RESERVATION =========================
    def finalize_reservation(self, reservation: Reservation):
        reservation.status = ReservationStatus.PENDING
        db.session.commit()

    # ========================= VALIDATE DATETIMES =========================
    def parse_dates(self, pickup_str: str, return_str: str):
        if not pickup_str or not return_str:
            raise ValueError("Please provide both pickup and return dates.")

        try:
            pickup = datetime.fromisoformat(pickup_str)
            dropoff = datetime.fromisoformat(return_str)
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        if pickup.date() < datetime.now().date():
            raise ValueError("Pickup date cannot be in the past.")
        if dropoff <= pickup:
            raise ValueError("Return date must be after pickup date.")

        return pickup, dropoff

    # ========================= CHECK AVAILABILITY =========================
    def is_car_available(self, vehicle_id: int, pickup: datetime, dropoff: datetime, exclude_reservation_id: int | None = None) -> bool:
        q = (
            Reservation.query
            .filter(
                Reservation.vehicle_id == vehicle_id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.ACTIVE]),
                Reservation.pickup_date < dropoff,
                Reservation.return_date > pickup
            )
        )


        # Exclude the reservation we're editing
        if exclude_reservation_id is not None:
            q = q.filter(Reservation.reservation_id != exclude_reservation_id)

        return q.first() is None
    
    # ========================= DELETE RESERVATION =========================
    def deletereservation(self, user_id, reservation_id):
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({"ok": False, "error": "Reservation not found"}), 404
        
        # Ownership check
        if reservation.user_id != user_id:
            return jsonify({"ok": False, "error": "Forbidden"}), 403
        
        # Delete
        db.session.delete(reservation)
        db.session.commit()

        return jsonify({"ok": True, "deleted_reservation_id": reservation_id})
    
    # ========================= EDIT RESERVATION =========================
    def edit_reservation(self, user_id, reservation_id, pickup_date_s: str, return_date_s: str):
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return jsonify({"ok": False, "error": "Reservation not found"}), 404
        
        # Ownership check
        if reservation.user_id != user_id:
            return jsonify({"ok": False, "error": "Forbidden"}), 403
        
        #Parse and validate dates
        pickup_date, return_date = self.parse_dates(pickup_date_s, return_date_s)

        # CHeck avalability
        if not self.is_car_available(reservation.vehicle_id, pickup_date, return_date, reservation.reservation_id):
            return jsonify({"ok": False, "error": "Vehicle not available for these dates"}), 409
        
        #Get latest daily rate for this vehicle
        price_row = (
            RentPrice.query
            .filter(RentPrice.vehicle_id == reservation.vehicle_id)
            .order_by(RentPrice.date.desc())
            .first()
        )
        daily_rate = price_row.price if price_row else 0.0
        #Calculate total amount
        days = (return_date - pickup_date).days
        # At least one day billing
        if days <= 0:
            days = 1  
        
        total_amount = daily_rate * days

        #Apply changes
        reservation.pickup_date = pickup_date
        reservation.return_date = return_date
        reservation.total_amount = total_amount
        db.session.commit()

        return jsonify({
            "ok": True,
            "reservation_id": reservation.reservation_id,
            "pickup_date": reservation.pickup_date.isoformat(),
            "return_date": reservation.return_date.isoformat(),
            "total_amount": str(reservation.total_amount),
            "days": days
        }), 200
    