import sqlite3

conn = sqlite3.connect("database/airsense.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM air_quality")
rows = cursor.fetchall()

if rows:
    print("\n📊 Air Quality Records:\n")
    for row in rows:
        print(row)
else:
    print("No records found.")

conn.close()