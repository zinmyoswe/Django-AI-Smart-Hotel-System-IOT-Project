import os
import json
import pika
import psycopg2
import psycopg2.extras
import requests
from dotenv import load_dotenv

load_dotenv()

QUEUE_NAME = "iot_data"

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "iotdb")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "latest_sensor_data")

def ensure_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS raw_data (
        timestamp BIGINT,
        datetime TIMESTAMPTZ,
        device_id TEXT,
        datapoint TEXT,
        value TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS iaq_readings (
        id SERIAL PRIMARY KEY,
        device_id TEXT,
        timestamp BIGINT,
        datetime TIMESTAMPTZ,
        temperature DOUBLE PRECISION,
        humidity DOUBLE PRECISION,
        co2 DOUBLE PRECISION
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS presence_readings (
        id SERIAL PRIMARY KEY,
        device_id TEXT,
        timestamp BIGINT,
        datetime TIMESTAMPTZ,
        presence_state TEXT,
        sensitivity INT,
        online_status TEXT
    );
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS power_readings (
        id SERIAL PRIMARY KEY,
        device_id TEXT,
        timestamp BIGINT,
        datetime TIMESTAMPTZ,
        power_kw DOUBLE PRECISION
    );
    """)

def connect_db():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    conn.autocommit = True
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    ensure_tables(cur)
    return conn, cur

def upsert_supabase(device_id, datapoints):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return
    url = f"{SUPABASE_URL}/rest/v1/{SUPABASE_TABLE}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates"
    }
    payload = {
        "device_id": device_id,
        "latest_data": json.dumps(datapoints)
    }
    r = requests.post(url, headers=headers, json=payload)
    try:
        r.raise_for_status()
    except Exception as e:
        print("[WARN] Supabase upsert failed:", e, "status:", r.status_code, "resp:", r.text)

def handle_message(cur, payload):
    ts = payload.get("timestamp")
    dt = payload.get("datetime")
    device_id = payload.get("device_id")
    datapoints = payload.get("datapoints", {})

    # Insert into device-specific table
    if device_id.startswith("iaq_sensor_"):
        cur.execute(
            "INSERT INTO iaq_readings (device_id, timestamp, datetime, temperature, humidity, co2) VALUES (%s, %s, %s, %s, %s, %s)",
            (device_id, ts, dt, datapoints.get("temperature"), datapoints.get("humidity"), datapoints.get("co2"))
        )
    elif device_id.startswith("presence_sensor_"):
        cur.execute(
            "INSERT INTO presence_readings (device_id, timestamp, datetime, presence_state, sensitivity, online_status) VALUES (%s, %s, %s, %s, %s, %s)",
            (device_id, ts, dt, datapoints.get("presence_state"), int(float(datapoints.get("sensitivity"))), datapoints.get("online_status"))
        )
    elif device_id.startswith("power_meter_"):
        cur.execute(
            "INSERT INTO power_readings (device_id, timestamp, datetime, power_kw) VALUES (%s, %s, %s, %s)",
            (device_id, ts, dt, datapoints.get("power_kw"))
        )

    # Insert each datapoint into raw_data
    for key, value in datapoints.items():
        cur.execute(
            "INSERT INTO raw_data (timestamp, datetime, device_id, datapoint, value) VALUES (%s, %s, %s, %s, %s)",
            (ts, dt, device_id, key, str(value))
        )

    upsert_supabase(device_id, datapoints)

def main():
    conn, cur = connect_db()

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        try:
            payload = json.loads(body.decode("utf-8"))
            handle_message(cur, payload)
            print("[DATALOGGER] Inserted payload for", payload.get("device_id"))
        except Exception as e:
            print("[ERROR] processing message:", e)

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print("[DATALOGGER] Listening on queue:", QUEUE_NAME)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Stopping...")
    finally:
        try:
            channel.stop_consuming()
        except Exception:
            pass
        connection.close()
        conn.close()

if __name__ == "__main__":
    main()
