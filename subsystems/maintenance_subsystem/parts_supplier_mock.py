from time import sleep
import requests

from random import randint, choice
from string import ascii_uppercase, digits
from datetime import datetime, timedelta


def generate_string(length):
    s = ''
    for i in range(length):
        s += choice(ascii_uppercase + digits)
    return s

secret_key = "secret_key"
def main():
    while True:
        order = requests.get('http://127.0.0.1:5000/maintenance/get_pending', json={"secret_key": secret_key})
        data = order.json()
        if not list(data.keys()):
            sleep(5)
            continue
        order_id = list(data.keys())[0]

        for component_id in data[order_id].keys():
            data[order_id][component_id]["price"] = randint(1, 100)
            data[order_id][component_id]["name"] = data[order_id][component_id]["name"] + f" ({generate_string(8)})"

        data["date"] = datetime.today()
        data["date"] += timedelta(days=1)
        data["date"] = str(data["date"])

        data["secret_key"] = "secret_key"

        update_request = requests.post('http://127.0.0.1:5000/maintenance/ship', json=data)

        sleep(5)


if __name__ == "__main__":
    main()
