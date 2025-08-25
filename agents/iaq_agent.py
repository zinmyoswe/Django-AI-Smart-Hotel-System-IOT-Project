import pika
import json
import time
import csv
import sys
from pathlib import Path

PUBLISH_INTERVAL = 5  # seconds
QUEUE_NAME = "iot_data"

def main():
    if len(sys.argv) < 2:
        print("Usage: python iaq_agent.py <RoomID>  # e.g., Room101")
        sys.exit(1)
    room_id = sys.argv[1]

    csv_path = Path(__file__).resolve().parent.parent / "data" / f"sample_iaq_data_{room_id}.csv"
    if not csv_path.exists():
        print(f"[ERROR] CSV not found: {csv_path}")
        sys.exit(1)

    connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            payload = {
                "device_id": f"iaq_sensor_{room_id}",
                "timestamp": int(time.time()),
                "datetime": row["datetime"],
                "datapoints": {
                    "temperature": row["temperature"],
                    "humidity": row["humidity"],
                    "co2": row["co2"],
                },
            }
            channel.basic_publish(exchange="", routing_key=QUEUE_NAME, body=json.dumps(payload))
            print(f"[IAQ:{room_id}] Published: {payload}")
            time.sleep(PUBLISH_INTERVAL)

    connection.close()

if __name__ == "__main__":
    main()