from api.fetch_data import fetch_air_quality
from database.database import create_database, save_air_quality

create_database()

LAT = 17.6868
LON = 83.2185
CITY = "Visakhapatnam"

data = fetch_air_quality(LAT, LON)

if data:
    save_air_quality(CITY, LAT, LON, data)
    print("✅ Data Saved Successfully!")
else:
    print("❌ Failed to fetch data.")