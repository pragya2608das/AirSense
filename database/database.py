import sqlite3

DB_NAME = "database/airsense.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS air_quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            latitude REAL,
            longitude REAL,
            timestamp INTEGER,
            aqi INTEGER,
            pm25 REAL,
            pm10 REAL,
            no2 REAL,
            co REAL,
            o3 REAL,
            so2 REAL
        )
    """)

    conn.commit()
    conn.close()


def save_air_quality(city, lat, lon, data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    info = data["list"][0]

    cursor.execute("""
        INSERT INTO air_quality (
            city,
            latitude,
            longitude,
            timestamp,
            aqi,
            pm25,
            pm10,
            no2,
            co,
            o3,
            so2
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        city,
        lat,
        lon,
        info["dt"],
        info["main"]["aqi"],
        info["components"]["pm2_5"],
        info["components"]["pm10"],
        info["components"]["no2"],
        info["components"]["co"],
        info["components"]["o3"],
        info["components"]["so2"]
    ))

    conn.commit()
    conn.close()


def get_city_history(city):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            timestamp,
            aqi,
            pm25,
            pm10,
            no2,
            co,
            o3,
            so2
        FROM air_quality
        WHERE city=?
        ORDER BY timestamp
    """, (city,))

    rows = cursor.fetchall()
    conn.close()

    return rows


def get_latest_city_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM air_quality
        WHERE id IN (
            SELECT MAX(id)
            FROM air_quality
            GROUP BY city
        )
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows
def get_total_records():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM air_quality")

    count = cursor.fetchone()[0]

    conn.close()

    return count
def get_average_aqi():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT AVG(aqi) FROM air_quality")

    avg = cursor.fetchone()[0]

    conn.close()

    return round(avg, 2)
def get_latest_all_cities():

    conn = sqlite3.connect(DB_NAME)

    query = """

    SELECT city,aqi

    FROM air_quality

    WHERE id IN (

        SELECT MAX(id)

        FROM air_quality

        GROUP BY city

    )

    """

    rows = conn.execute(query).fetchall()

    conn.close()

    return rows