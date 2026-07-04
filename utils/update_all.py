from api.fetch_data import fetch_air_quality
from database.database import save_air_quality

def update_all_cities(locations):

    for city, (lat, lon) in locations.items():

        data = fetch_air_quality(lat, lon)

        if data:
            save_air_quality(city, lat, lon, data)