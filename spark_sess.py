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

windowedAvg = stream_data.withWatermark("timestamp", "30 minutes").groupBy(
	window(stream_data.timestamp, "10 minutes")
).avg()

windowedAvailability = stream_data.withWatermark("timestamp", "30 minutes").groupBy(
	window(stream_data.timestamp, "30 minutes")
).count()


rawQuery = stream_data.withColumn('value', to_json(struct(*stream_data.columns), options={"ignoreNullFields":False})).select("value").writeStream.format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("checkpointLocation", "~/kafka-checkpoint/raw/").option("topic", "real_time_viz_raw").start()

avgQuery = windowedAvg.withColumn('value', to_json(struct(*windowedAvg.columns), options={"ignoreNullFields":False})).select("value").writeStream.outputMode("complete").format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("checkpointLocation", "~/kafka-checkpoint/avg/").option("topic", "real_time_viz_avg").start()
						  
availabilityQuery = windowedAvailability.withColumn('value', to_json(struct(*windowedAvailability.columns), options={"ignoreNullFields":False})).select("value").writeStream.outputMode("complete").format("kafka").option("kafka.bootstrap.servers", "localhost:9092").option("checkpointLocation", "~/kafka-checkpoint/avail/").option("topic", "real_time_viz_avail").start()

spark.streams.awaitAnyTermination()
