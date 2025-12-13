from datetime import datetime
import uuid
from sqlalchemy import or_, and_
from models.User import User
from models.Vehicle import Vehicle
from models.Reservation import Reservation
from models.InsurancePolicy import InsurancePolicy
from context import db

class ReservationSubsystem:
    def __init__(self):
        pass

    def create_reservation(self, user: User, vehicle: Vehicle, pickup_date_s: str, return_date_s: str) -> Reservation:
        #Parse and validate dates
        pickup_date, return_date = self.parse_dates(pickup_date_s, return_date_s)
        
        #Check availability
        if not self.is_car_available(vehicle.id, pickup_date, return_date):
            raise ValueError("The selected vehicle is not available for the chosen dates.")

        #Calculate total amount
        days = (return_date - pickup_date).days
        total_amount = vehicle.daily_rate * days

        #Create reservation record
        reservation = Reservation(
            reservation_id=str(uuid.uuid4()),
            user_id=user.user_id,
            vehicle_id=vehicle.vehicle_id,
            total_amount=total_amount,
            pickup_date=pickup_date,
            return_date=return_date,
            status=Reservation.ReservationStatus.PENDING
        )
        db.session.add(reservation)
        db.session.commit()

        return reservation

    def add_insurance_to_reservation(self, reservation: Reservation, provider: str, amount: float) -> InsurancePolicy:
        #Create insurance policy
        policy = self.create_insurance_policy(
            insurance_id=str(uuid.uuid4()),
            reservation_id=reservation.reservation_id,
            provider=provider,
            payment_amount=amount,
            start_date=reservation.pickup_date,
            end_date=reservation.return_date,
            policy_number=f"POL-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{reservation.reservation_id[:6]}"
        )

        db.session.add(policy)
        db.session.commit()

        return policy

    def finalize_reservation(self, reservation: Reservation):
        reservation.status = Reservation.ReservationStatus.CONFIRMED
        db.session.commit()

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
    def is_car_available(self, car_id: int, pickup: datetime, dropoff: datetime) -> bool:
        overlapping = (
            Reservation.query.filter(
                Reservation.car_id == car_id,
                Reservation.status != Reservation.status.CANCELLED,
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