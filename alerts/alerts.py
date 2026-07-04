def generate_alert(aqi):

    if aqi >= 5:

        return (
            "🔴 Severe",
            "Avoid outdoor activities. Wear an N95 mask."
        )

    elif aqi == 4:

        return (
            "🟠 Poor",
            "Sensitive groups should remain indoors."
        )

    elif aqi == 3:

        return (
            "🟡 Moderate",
            "Limit prolonged outdoor exposure."
        )

    elif aqi == 2:

        return (
            "🟢 Fair",
            "Air quality is acceptable."
        )

    else:

        return (
            "🟢 Good",
            "Enjoy outdoor activities."
        )