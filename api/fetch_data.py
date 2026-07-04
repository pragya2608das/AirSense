import requests
from config import OPENWEATHER_API_KEY

BASE_URL = "http://api.openweathermap.org/data/2.5/air_pollution"


def fetch_air_quality(lat, lon):
    """
    Fetch live air quality data for a given latitude and longitude.
    """

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHER_API_KEY
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        return response.json()

    return None