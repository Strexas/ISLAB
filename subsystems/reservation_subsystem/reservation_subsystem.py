from datetime import datetime
from models.User import User
from models.Vehicle import Vehicle
from models.Reservation import Reservation, ReservationStatus
from models.InsurancePolicy import InsurancePolicy
from models.RentPrice import RentPrice
from context import db
import uuid

class ReservationSubsystem:
    def __init__(self):
        pass

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
        total_amount = daily_rate * days

        #Create reservation record
        reservation = Reservation(
            user_id=user.id,
            vehicle_id=vehicle.id,
            total_amount=total_amount,
            pickup_date=pickup_date,
            return_date=return_date,
            status=ReservationStatus.PENDING
        )

        db.session.add(reservation)
        db.session.flush()
        
        return reservation

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

    def finalize_reservation(self, reservation: Reservation):
        reservation.status = ReservationStatus.PENDING
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
    def is_car_available(self, vehicle_id: int, pickup: datetime, dropoff: datetime) -> bool:
        overlapping = (
            Reservation.query
            .filter(
                Reservation.vehicle_id == vehicle_id,
                Reservation.status.in_([ReservationStatus.PENDING, ReservationStatus.ACTIVE]),
                Reservation.pickup_date < dropoff,
                Reservation.return_date > pickup
            )
            .first()
        )

        return overlapping is None