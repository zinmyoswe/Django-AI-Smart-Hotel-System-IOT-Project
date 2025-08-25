import pika
import json
import time
import csv
from pathlib import Path

PUBLISH_INTERVAL = 5  # seconds
QUEUE_NAME = "iot_data"

def main():
    # Load CSV file
    csv_path = Path(__file__).resolve().parent.parent / "data" / "sample_power_meter_data.csv"
    if not csv_path.exists():
        print(f"[ERROR] CSV not found: {csv_path}")
        return

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    with csv_path.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            for meter_id in range(1, 7):  # Loop through all 6 meters
                column_name = f"power_kw_power_meter_{meter_id}"
                try:
                    payload = {
                        "device_id": f"power_meter_{meter_id}",
                        "timestamp": int(time.time()),
                        "datetime": row["datetime"],
                        "datapoints": {
                            "power_kw": float(row[column_name])
                        }
                    }
                    channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=json.dumps(payload))
                    print(f"[ROW {idx} POWER:{meter_id}] Published: {payload}")
                    time.sleep(PUBLISH_INTERVAL)
                except Exception as e:
                    print(f"[ERROR ROW {idx} POWER:{meter_id}] {e}")
                    continue

    connection.close()
    print("[INFO] Finished publishing all meters for all datetimes.")

if __name__ == "__main__":
    main()
