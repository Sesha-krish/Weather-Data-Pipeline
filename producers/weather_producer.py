import os, json, time, requests
from kafka import KafkaProducer
from datetime import datetime

# Get API key from env var (sign up free at https://openweathermap.org/)
API_KEY = "d5878c144d04bfa727ddfce0d98966a0"
CITY = "London"
URL = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"

producer = KafkaProducer(
    bootstrap_servers="localhost:29092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8"),
)

TOPIC = "weather-data"

def fetch_weather():
    try:
        resp = requests.get(URL)
        data = resp.json()
        return {
            "city": CITY,
            "timestamp": datetime.utcnow().isoformat(),
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"]
        }
    except Exception as e:
        print("Error fetching weather:", e)
        return None

if __name__ == "__main__":
    while True:
        weather = fetch_weather()
        if weather:
            producer.send(TOPIC, weather)
            print("Sent:", weather)
        time.sleep(3)  # fetch every 30s
