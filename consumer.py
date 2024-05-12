from kafka import KafkaConsumer
import json
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, explode, col
from pyspark.sql.types import ArrayType, FloatType
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.recommendation import ALS
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import StringIndexer
from pyspark.sql.functions import col

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Song Recommendation Consumer") \
    .config("spark.mongodb.input.uri", "mongodb://127.0.0.1/music2_database.music2_collection") \
    .config("spark.mongodb.output.uri", "mongodb://127.0.0.1/music2_database.music2_collection") \
    .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1") \
    .getOrCreate()

# Load model and necessary data
df = spark.read.format("com.mongodb.spark.sql.DefaultSource").load()
df = df.dropna(subset=["_id", "id"])

def string_to_float_list(string):
    return [float(x.strip()) for x in string.strip('[]').split(',')]

string_to_float_list_udf = udf(string_to_float_list, ArrayType(FloatType()))
df = df.withColumn("feature", string_to_float_list_udf(df["feature"]))

indexer1 = StringIndexer(inputCol="_id", outputCol="UserId")
indexer2 = StringIndexer(inputCol="id", outputCol="AudioId")
df = indexer1.fit(df).transform(df)
df = indexer2.fit(df).transform(df)

exploded_df = df.select("UserId", "AudioId", explode("feature").alias("feature_value"))
exploded_df = exploded_df.withColumn("feature_value", col("feature_value").cast("float"))
assembler = VectorAssembler(inputCols=["feature_value"], outputCol="features")
data = assembler.transform(exploded_df)

# Train collaborative filtering model
als = ALS(rank=10, maxIter=10, regParam=0.01, userCol="UserId", itemCol="AudioId", ratingCol="feature_value")
model = als.fit(data)

# Initialize Kafka consumer
consumer = KafkaConsumer('similar-songs-topic', bootstrap_servers='localhost:9092',
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))


for message in consumer:
    track_id = message.value
    filtered_df = df.filter(col('id') == track_id)
    if filtered_df.count() > 0:
        user_ids = filtered_df.select('UserId').collect()
        saim = user_ids[0]['UserId']
        
        userSubset = spark.createDataFrame([(saim,)], ["UserId"])
        recommendations = model.recommendForUserSubset(userSubset, 10)

        recommendations = recommendations.select("UserId", explode("recommendations").alias("recommendation"))
        recommendations = recommendations.select("UserId", "recommendation.AudioId", "recommendation.rating")

        recommendations_with_title = recommendations.join(df, recommendations.AudioId == df.AudioId)
        recommendations_with_title = recommendations_with_title.select("id")

        with open("similar.txt", "w") as file:
            for row in recommendations_with_title.collect():
                file.write(f"{row['id']}\n")
    
    

# Close Kafka consumer
consumer.close()
spark.stop()
