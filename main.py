import requests
from datetime import datetime
import smtplib
import time
import os

# Environment variables
MY_EMAIL = os.getenv("MY_EMAIL")
MY_PASSWORD = os.getenv("MY_PASSWORD")

# Your location (change if needed)
MY_LAT = 51.507351     # Latitude
MY_LONG = -0.127758   # Longitude


def is_iss_overhead():
    """Check if ISS is within ±5 degrees of current location."""
    response = requests.get("http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()

    iss_latitude = float(data["iss_position"]["latitude"])
    iss_longitude = float(data["iss_position"]["longitude"])

    return (
        MY_LAT - 5 <= iss_latitude <= MY_LAT + 5 and
        MY_LONG - 5 <= iss_longitude <= MY_LONG + 5
    )


def is_night():
    """Check if it is currently nighttime at the given location."""
    parameters = {
        "lat": MY_LAT,
        "lng": MY_LONG,
        "formatted": 0
    }

    response = requests.get(
        "https://api.sunrise-sunset.org/json",
        params=parameters
    )
    response.raise_for_status()
    data = response.json()

    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now = datetime.now().hour
    return time_now >= sunset or time_now <= sunrise


def send_email():
    """Send an email alert."""
    with smtplib.SMTP("smtp.gmail.com", 587) as connection:
        connection.starttls()
        connection.login(MY_EMAIL, MY_PASSWORD)
        connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg="Subject:Look Up \n\nThe ISS is above you in the sky!"
        )


if __name__ == "__main__":
    email_sent = False

    while True:
        time.sleep(60)
        if is_iss_overhead() and is_night() and not email_sent:
            send_email()
            email_sent = True
