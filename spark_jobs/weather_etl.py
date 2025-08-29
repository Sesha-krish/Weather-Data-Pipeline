from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# Initialize Spark with MinIO configs
spark = SparkSession.builder \
    .appName("WeatherETL") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Define schema of raw JSON
schema = StructType([
    StructField("city", StringType(), True),
    StructField("temperature", DoubleType(), True),
    StructField("humidity", DoubleType(), True),
    StructField("wind_speed", DoubleType(), True),
    StructField("pressure", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])

# Read raw data from MinIO bucket
raw_df = spark.read.json("s3a://weather-bucket/raw/weather/*.json", schema=schema)

# Basic cleaning (drop nulls, convert temperature to Celsius)
clean_df = raw_df.dropna().withColumn("temperature_C", col("temperature") - 273.15)

# Write transformed data back to MinIO in parquet format
clean_df.write.mode("overwrite").parquet("s3a://weather-bucket/curated/weather/")
