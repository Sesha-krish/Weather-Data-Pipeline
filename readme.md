# Weather Data Pipeline (ETL with Spark, Airflow, MinIO, Docker)

This project implements an **end-to-end Data Engineering pipeline** that ingests live weather data, stores it in an object store (MinIO/S3), processes it using Spark, and orchestrates the workflow with Apache Airflow.  

The goal is to demonstrate a **real-world style data pipeline** using open-source tools.

---

## Workflow Overview

1. **Data Source (OpenWeather API)**
   - We fetch live weather data from the OpenWeather API.
   - The raw JSON responses are stored in MinIO (acts as S3 storage).

2. **Storage (MinIO / S3)**
   - MinIO is used as a local S3-compatible object store.
   - Raw JSON files are written under `raw/weather/`.
   - Processed/cleaned Parquet files are written under `processed/weather/`.

3. **Processing (Apache Spark)**
   - Spark ETL job (`weather_etl.py`) reads the raw JSON data from MinIO.
   - Cleans and transforms the data (extracts fields like temperature, humidity, windspeed, etc.).
   - Stores the processed data back into MinIO in **Parquet** format for downstream use.

4. **Orchestration (Apache Airflow)**
   - Airflow DAG (`weather_dag.py`) automates the workflow:
     - **Task 1:** Fetch weather data and upload raw JSON → MinIO
     - **Task 2:** Submit the Spark ETL job → clean + process data
   - Ensures tasks run in order and can be scheduled daily/hourly.

5. **Deployment (Docker + docker-compose)**
   - All services run inside Docker containers:
     - Spark Master + Worker
     - Airflow Scheduler + Webserver
     - MinIO server
     - PostgreSQL (Airflow backend DB)
   - This makes the entire pipeline reproducible on any system.

---

## Project Structure

weather-data-pipeline/
│
├── dags/
│ └── weather_dag.py # Airflow DAG to orchestrate pipeline
│
├── spark_jobs/
│ └── weather_etl.py # Spark job for ETL processing
│
├── docker-compose.yml # Docker services (Airflow, Spark, MinIO, Postgres)
├── requirements.txt # Python dependencies (Airflow operators, boto3, etc.)
├── README.txt 

## Setup & Run

### 1. Clone the Repository
```bash
git clone https://github.com/Sesha-krish/Weather-Data-Pipeline.git
cd Weather-Data-Pipeline
```
### 2.Start Services with Docker
```bash
docker-compose up -d 
``` 

This will start:

Airflow Scheduler + Webserver (http://localhost:8080)

Spark Master (spark://spark-master:7077)

MinIO (http://localhost:9000, console: http://localhost:9001)

### 3.Installing dependencies 
```bash
pip install -r requirements.txt
```
### 4. Environment Variables 
You need to login into openweather.org and get a free api key and replace it in the .env file along with your minio credentials 
eg: 
```bash 
OPENWEATHER_API_KEY="   YOUR OPENWEATHER API KEY"
MINIO_ENDPOINT = "localhost:9000"
MINIO_ACCESS_KEY = "youraccessname"
MINIO_SECRET_KEY = "youraccesspassword"
```
### 5.Try running the producer to see if the producer is sending data to the Kafka Broker 

```bash
python producers/weather_producer.py
```
if you can see the json responses flowing, we can test the consumer 

### 6.Try running the consumer to see if the consumer is receiving messages 

```bash 
python consumers/weather_consumer.py 
``` 

if it succeeds, the next job is to build the spark job 

### 7. Create the Spark job for ETL 
```bash
docker exec -it spark-master bash -c "spark-submit \                     
   --master spark://spark-master:7077 \ 
   /opt/spark_jobs/weather_etl.py" 
```

### 8. Login into your MinIO UI to see the transformed data in your bucket

login into localhost:9001 with your minio credentials