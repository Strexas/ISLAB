from models.Reservation import Reservation

class ReservationSubsystem:
    def __init__(self):
        pass

    def create_reservation(self, user_id, car_id, start_date, end_date):
        # Logic to create a reservation
        pass
    
    def get_reservations(self, user_id):
        reservations = Reservation.query.filter_by(user_id=user_id).all()
        return reservations