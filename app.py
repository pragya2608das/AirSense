import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_folium import st_folium
from forecast.forecast import predict_next_aqi
from utils.map_utils import create_map

from database.database import (
    get_latest_city_data,
    get_total_records,
    get_average_aqi,
    get_latest_all_cities
)
from api.fetch_data import fetch_air_quality

from database.database import (
    save_air_quality,
    get_city_history,
)

from data.cities import LOCATIONS


# ---------------------------------------------------------
# ALERT LOGIC
# ---------------------------------------------------------

def generate_alert(aqi):
    """
    Takes an AQI value (1-5 scale from OpenWeatherMap)
    and returns a (level, message) tuple.
    """
    alert_map = {
        1: ("🟢 Good", "Air quality is good. No action needed."),
        2: ("🟡 Fair", "Air quality is acceptable. Sensitive groups should monitor conditions."),
        3: ("🟠 Moderate", "Sensitive groups should reduce prolonged outdoor exertion."),
        4: ("🔴 Poor", "Health alert: everyone may experience health effects. Limit outdoor activity."),
        5: ("🟣 Very Poor", "Health warning: emergency conditions. Avoid outdoor activity and notify municipal officers."),
    }

    aqi_rounded = int(round(aqi))
    return alert_map.get(
        aqi_rounded,
        ("⚪ Unknown", "AQI data unavailable or out of range.")
    )


# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------

st.set_page_config(
    page_title="AirSense",
    page_icon="🌍",
    layout="wide"
)


# ---------------------------------------------------------
# LOAD CSS
# ---------------------------------------------------------

def load_css():
    with open("assets/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()


# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------

st.sidebar.title("🌍 AirSense")
st.sidebar.markdown("### Smart Air Quality Monitoring")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "🗺 India Map",
        "📈 Analytics",
        "🔮 Forecast",
        "🚨 Air Quality Alerts"
    ]
)

# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

if page == "📊 Dashboard":

    city = st.sidebar.selectbox(
        "📍 Select City",
        list(LOCATIONS.keys())
    )

    lat, lon = LOCATIONS[city]

    st.sidebar.success(
        f"Selected City:\n\n{city}"
    )

    if st.sidebar.button("🔄 Refresh Selected City"):
        st.rerun()

    analyze_all = st.sidebar.button(
        "🌍 Analyze All Cities"
    )

    # -----------------------------------------------------
    # HEADER
    # -----------------------------------------------------

    st.title("🌍 AirSense")

    st.markdown("""
## Smart Air Quality Monitoring & Early Warning System

Real-time air quality monitoring,
historical analytics,
forecasting and municipal alerts.
""")

    st.caption(
        f"Last Updated: {datetime.now().strftime('%d %b %Y %I:%M:%S %p')}"
    )

    st.divider()

    # -----------------------------------------------------
    # FETCH LIVE DATA
    # -----------------------------------------------------

    data = fetch_air_quality(lat, lon)

    if data:
        save_air_quality(
            city,
            lat,
            lon,
            data
        )

    # -----------------------------------------------------
    # SHOW LIVE DATA
    # -----------------------------------------------------

    if data:

        info = data["list"][0]

        components = info["components"]

        aqi = info["main"]["aqi"]

        st.subheader("📊 Current Air Quality")

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("AQI", aqi)
        c2.metric("PM2.5", components["pm2_5"])
        c3.metric("PM10", components["pm10"])
        c4.metric("NO₂", components["no2"])
        c5.metric("CO", components["co"])

        # -----------------------------------------------
        # AQI STATUS
        # -----------------------------------------------

        status = {
            1: ("🟢", "Good"),
            2: ("🟡", "Fair"),
            3: ("🟠", "Moderate"),
            4: ("🔴", "Poor"),
            5: ("🟣", "Very Poor")
        }

        emoji, text = status.get(aqi, ("⚪", "Unknown"))

        st.success(f"{emoji} Air Quality Status : **{text}**")

        # -----------------------------------------------------
        # POLLUTANT LEVELS CHART
        # -----------------------------------------------------

        st.divider()

        st.subheader("📈 Current Pollutant Levels")

        pollutants = pd.DataFrame({
            "Pollutant": ["PM2.5", "PM10", "NO₂", "CO", "O₃", "SO₂"],
            "Value": [
                components["pm2_5"],
                components["pm10"],
                components["no2"],
                components["co"],
                components["o3"],
                components["so2"]
            ]
        })

        fig = px.bar(
            pollutants,
            x="Pollutant",
            y="Value",
            color="Pollutant",
            text_auto=".2f",
            title="Current Pollutant Levels"
        )

        st.plotly_chart(fig, use_container_width=True)

        # -----------------------------------------------------
        # HISTORICAL DATA
        # -----------------------------------------------------

        st.divider()

        history = get_city_history(city)

        if history:

            history_df = pd.DataFrame(
                history,
                columns=[
                    "Timestamp", "AQI", "PM25", "PM10",
                    "NO2", "CO", "O3", "SO2"
                ]
            )

            history_df["Timestamp"] = pd.to_datetime(
                history_df["Timestamp"], unit="s"
            )

            st.subheader("📉 AQI History")

            history_chart = px.line(
                history_df,
                x="Timestamp",
                y="AQI",
                markers=True,
                title=f"{city} AQI Trend"
            )

            st.plotly_chart(history_chart, use_container_width=True)

            # -------------------------------------------------
            # DATABASE SUMMARY
            # -------------------------------------------------

            st.divider()

            st.subheader("📊 Database Summary")

            d1, d2, d3 = st.columns(3)

            d1.metric("Records Stored", len(history_df))
            d2.metric("Latest AQI", history_df.iloc[-1]["AQI"])
            d3.metric("Average AQI", round(history_df["AQI"].mean(), 2))

        else:
            st.info("No historical data available yet.")

        # =====================================================
        # LIVE INDIA MAP
        # =====================================================

        st.divider()

        st.subheader("🗺 Live Air Quality Map")

        latest = get_latest_city_data()

        city_data = []

        for row in latest:
            city_data.append({
                "city": row[1],
                "lat": row[2],
                "lon": row[3],
                "aqi": row[5],
                "pm25": row[6],
                "pm10": row[7],
                "no2": row[8],
                "co": row[9]
            })

        india_map = create_map(city_data)

        st_folium(india_map, width=1200, height=600)

        # =====================================================
        # ANALYZE ALL CITIES
        # =====================================================

        if analyze_all:

            st.divider()

            st.header("🇮🇳 National Air Quality Analysis")

            records = get_total_records()
            avg_aqi = get_average_aqi()
            cities = get_latest_all_cities()

            highest = max(cities, key=lambda x: x[1])
            lowest = min(cities, key=lambda x: x[1])

            c1, c2, c3, c4 = st.columns(4)

            c1.metric("Cities Monitored", len(cities))
            c2.metric("Total Records", records)
            c3.metric("Average AQI", avg_aqi)
            c4.metric("Highest AQI", highest[1])

            # --------------------------------------------
            # Ranking Table
            # --------------------------------------------

            ranking = pd.DataFrame(cities, columns=["City", "AQI"])
            ranking = ranking.sort_values(by="AQI", ascending=False)

            st.subheader("🏆 City AQI Ranking")

            st.dataframe(ranking, use_container_width=True)

            # --------------------------------------------
            # Comparison Chart
            # --------------------------------------------

            chart = px.bar(
                ranking,
                x="City",
                y="AQI",
                color="AQI",
                text_auto=True,
                title="Current AQI Comparison"
            )

            st.plotly_chart(chart, use_container_width=True)

            # --------------------------------------------
            # Insights
            # --------------------------------------------

            st.subheader("🌍 Air Quality Insights")

            st.success(f"🌿 Cleanest City : {lowest[0]} (AQI {lowest[1]})")
            st.error(f"🏭 Most Polluted City : {highest[0]} (AQI {highest[1]})")

            # --------------------------------------------
            # Download CSV
            # --------------------------------------------

            csv = ranking.to_csv(index=False)

            st.download_button(
                "📥 Download Analytics CSV",
                csv,
                file_name="airsense_analytics.csv",
                mime="text/csv"
            )

    else:
        st.error("Unable to fetch live AQI.")


# ==========================================================
# INDIA MAP PAGE
# ==========================================================

if page == "🗺 India Map":

    st.title("🗺 India Air Quality Map")

    latest = get_latest_city_data()

    city_data = []

    for row in latest:
        city_data.append({
            "city": row[1],
            "lat": row[2],
            "lon": row[3],
            "aqi": row[5],
            "pm25": row[6],
            "pm10": row[7],
            "no2": row[8],
            "co": row[9]
        })

    india_map = create_map(city_data)

    st_folium(india_map, width=1200, height=650)


# ==========================================================
# ANALYTICS PAGE
# ==========================================================

if page == "📈 Analytics":

    st.title("📈 National Analytics")

    records = get_total_records()
    avg_aqi = get_average_aqi()
    cities = get_latest_all_cities()

    highest = max(cities, key=lambda x: x[1])
    lowest = min(cities, key=lambda x: x[1])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Cities", len(cities))
    c2.metric("Records", records)
    c3.metric("Average AQI", avg_aqi)
    c4.metric("Highest AQI", highest[1])

    ranking = pd.DataFrame(cities, columns=["City", "AQI"])
    ranking = ranking.sort_values(by="AQI", ascending=False)

    st.subheader("🏆 AQI Ranking")

    st.dataframe(ranking, use_container_width=True)

    fig = px.bar(
        ranking,
        x="City",
        y="AQI",
        color="AQI",
        text_auto=True
    )

    st.plotly_chart(fig, use_container_width=True)

    st.success(f"🌿 Cleanest City : {lowest[0]}")
    st.error(f"🏭 Most Polluted City : {highest[0]}")

    csv = ranking.to_csv(index=False)

    st.download_button(
        "📥 Download CSV",
        csv,
        file_name="airsense_analytics.csv",
        mime="text/csv"
    )


# ==========================================================
# FORECAST PAGE
# ==========================================================

if page == "🔮 Forecast":

    st.title("🔮 AQI Forecast")

    city = st.selectbox(
        "Select City",
        list(LOCATIONS.keys())
    )

    predicted = predict_next_aqi(city)

    if predicted is not None:

        level, message = generate_alert(predicted)

        st.metric("Predicted AQI", predicted)

        st.warning(level)
        st.info(message)

    else:
        st.info("Not enough historical data.")


# ==========================================================
# ALERT PAGE
# ==========================================================

if page == "🚨 Air Quality Alerts":

    st.title("🚨 Air Quality Alerts")

    latest = get_latest_all_cities()

    alerts = 0

    for row in latest:

        city = row[0]
        aqi = row[1]

        level, message = generate_alert(aqi)

        if aqi >= 3:

            alerts += 1

            with st.container():
                st.error(f"### 📍 {city}")
                st.write(f"**AQI:** {aqi}")
                st.write(f"**Status:** {level}")
                st.info(message)

    if alerts == 0:
        st.success("✅ No active alerts.")