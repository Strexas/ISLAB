from datetime import datetime
from sqlalchemy import or_, and_
from models import Reservation, InsurancePolicy
from context import db

class ReservationSubsystem:
    def __init__(self):
        pass

    #Validate datetimes (Use Case: Make a Reservation)
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
    
    #Check car availability (Use Case: Make a Reservation)
    def is_car_available(self, car_id, pickup, dropoff) -> bool:
        overlapping = (
            Reservation.query.filter(
                Reservation.car_id == car_id,
                Reservation.status != Reservation.ReservationStatus.CANCELLED,
                or_(
                    # new start inside existing
                    and_(Reservation.pickup_date <= pickup,
                         Reservation.return_date > pickup),
                    # new end inside existing
                    and_(Reservation.pickup_date < dropoff,
                         Reservation.return_date >= dropoff),
                    # existing fully inside new range
                    and_(Reservation.pickup_date >= pickup,
                         Reservation.return_date <= dropoff),
                ),
            )
            .with_entities(Reservation.reservation_id)
            .first()
        )

        return overlapping is None
    
    def create_insurance_policy(self, user_id, car_id, pickup_date, return_date):
        policy = InsurancePolicy(
            customer_id=user_id,
            car_id=car_id,
            start_date=pickup_date,
            end_date=return_date,
            provider="Default",
            payment_amount=29.99, 
            policy_number=f"POL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{user_id[:6]}"
        )
        db.session.add(policy)
        db.session.flush()  # get policy id without full commit
        return policy