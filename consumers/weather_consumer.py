import json
import os
import time
from kafka import KafkaConsumer
from minio import Minio
from datetime import datetime

# Kafka settings
TOPIC = "weather_data"
KAFKA_BROKER = "localhost:29092"

# MinIO settings
MINIO_ENDPOINT = "localhost:9000"
MINIO_BUCKET = "weather-bucket"
MINIO_ACCESS_KEY = "minio"
MINIO_SECRET_KEY = "minio123"

# Create Kafka consumer
consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
    auto_offset_reset="earliest",  # read from beginning if no offset
    enable_auto_commit=True
)

# Create MinIO client
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Ensure bucket exists
if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)

print("🚀 Weather consumer started. Listening for messages...")

for message in consumer:
    weather_data = message.value

    # Save each record as JSON file
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_name = f"weather_{timestamp}.json"

    with open(file_name, "w") as f:
        json.dump(weather_data, f)

    # Upload file to MinIO
    minio_client.fput_object(MINIO_BUCKET, file_name, file_name)

    print(f"✅ Saved weather data to {file_name} and uploaded to MinIO bucket {MINIO_BUCKET}")

    # Optional: delete local file after upload
    os.remove(file_name)

    time.sleep(1)
