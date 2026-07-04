from database.database import get_city_history


def predict_next_aqi(city):

    history = get_city_history(city)

    if len(history) < 2:

        return None

    # Get AQI values
    aqi_values = [row[1] for row in history]

    latest = aqi_values[-1]

    previous = aqi_values[-2]

    # Trend

    change = latest - previous

    prediction = latest + change

    prediction = max(1, min(5, prediction))

    return prediction