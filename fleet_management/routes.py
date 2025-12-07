from flask import render_template, request, redirect, url_for
from . import fleet_bp
from models.Vehicle import Vehicle


FLEET = [
    {
        "id": "corolla-2020",
        "brand": "Toyota",
        "model": "Corolla 2020",
        "price_per_day": 45,
        "seats": 5,
        "fuel": "Petrol",
        "transmission": "Automatic",
        "image": "https://upload.wikimedia.org/wikipedia/commons/2/21/2019_Toyota_Corolla.jpg"
    },
    {
        "id": "tesla-s-2022",
        "brand": "Tesla",
        "model": "Model S 2022",
        "price_per_day": 180,
        "seats": 5,
        "fuel": "Electric",
        "transmission": "Automatic",
        "image": "https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_Model_S_02_2013.jpg"
    }
]

def get_car(car_id: str):
    for car in FLEET:
        if car["id"] == car_id:
            return car
    return None



@fleet_bp.route("/fleet")
def fleet_list():
    return render_template("fleetlist.html", cars=FLEET)


@fleet_bp.route("/fleet/<car_id>")
def car_details(car_id):
    car = get_car(car_id)
    if not car:
        abort(404)

    mock_status = {
        "status_text": "Available",
        "last_maintenance": "2024-08-12",
        "next_maintenance": "2025-01-05",
        "condition": "Good",
        "reservation_status": "Not Reserved",
        "mileage": "25,300 km"
    }

    return render_template("car_details.html", car=car, status=mock_status)


@fleet_bp.route("/fleet/add")
def add_car():
    # THIS WILL BE A MOCK PAGE — NO DB YET
    return render_template("add_car.html")