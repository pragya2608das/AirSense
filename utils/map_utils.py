import folium


def get_marker_color(aqi):

    colors = {
        1: "green",
        2: "blue",
        3: "orange",
        4: "red",
        5: "darkred"
    }

    return colors.get(aqi, "gray")


def create_map(city_data):

    india_map = folium.Map(
        location=[22.5, 79],
        zoom_start=5
    )

    for city in city_data:

        popup = f"""
        <b>{city['city']}</b><br>

        AQI : {city['aqi']}<br>

        PM2.5 : {city['pm25']}<br>
        PM10 : {city['pm10']}<br>
        NO₂ : {city['no2']}<br>
        CO : {city['co']}
        """

        folium.Marker(

            location=[city["lat"], city["lon"]],

            popup=popup,

            tooltip=city["city"],

            icon=folium.Icon(
                color=get_marker_color(city["aqi"]),
                icon="cloud"
            )

        ).add_to(india_map)

    return india_map