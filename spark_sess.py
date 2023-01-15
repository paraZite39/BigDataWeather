from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

if __name__ == "__main__":
	spark = (SparkSession.builder.appName("Big Data API")
			     .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2")
			     .master("local[*]")
			     .getOrCreate())
	spark.sparkContext.setLogLevel("WARN")
	
KAFKA_TOPIC_NAME = "realtime-stream"
KAFKA_BOOTSTRAP_SERVER = "localhost:9092"

df = (
	spark.readStream.format("kafka")
	.option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVER)
	.option("subscribe", KAFKA_TOPIC_NAME)
	.option("startingOffsets", "latest")
	.load()
)

# base_df = df.selectExpr("CAST(value as STRING)", "timestamp")
# base_df.printSchema()

stream_schema = StructType([
	StructField("timestamp", TimestampType(), True),
	StructField("temp", FloatType(), True),
	StructField("rain", FloatType(), True),
	StructField("flow", FloatType(), True),
	])

stream = df.select(from_json(col("value").cast("string"), stream_schema).alias("parsed_values"))
stream_data = stream.select("parsed_values.*")

windowedAvg = stream_data.withWatermark("timestamp", "10 minutes").groupBy(
	window(stream_data.timestamp, "10 minutes")
).avg().writeStream.outputMode("complete").format("console").start()

windowedAvailability = stream_data.withWatermark("timestamp", "30 minutes").groupBy(
	window(stream_data.timestamp, "30 minutes")
).count().writeStream.outputMode("complete").format("console").start()

windowedAvg.awaitTermination()
windowedAvailability.awaitTermination()
