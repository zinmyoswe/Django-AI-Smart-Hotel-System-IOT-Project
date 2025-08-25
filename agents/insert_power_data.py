import csv
import time
from datetime import datetime
import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "iotdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")

CSV_PATH = "data/sample_power_meter_data.csv"
FIXED_DATE = "2024-12-27"  # adjust if needed

def connect_db():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor()
    return conn, cur

def main():
    conn, cur = connect_db()
    inserted_count = 0

    with open(CSV_PATH, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            datetime_str = f"{FIXED_DATE} {row['datetime']}"
            try:
                dt_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M.%S")
            except ValueError:
                # fallback if format changes
                dt_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
            ts = int(time.mktime(dt_obj.timetuple()))

            for i in range(1, 7):
                key = f"power_kw_power_meter_{i}"
                value = row[key]
                if value.strip() == "":
                    continue

                cur.execute(
                    "INSERT INTO raw_data (timestamp, datetime, device_id, datapoint, value) VALUES (%s, %s, %s, %s, %s)",
                    (ts, dt_obj, f"power_meter_{i}", "power_kw", value)
                )
                inserted_count += 1

    conn.close()
    print(f"Inserted {inserted_count} power meter datapoints into raw_data.")

if __name__ == "__main__":
    main()
