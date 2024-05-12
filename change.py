import pandas as pd
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['music_database']
collection = db['audio_features']

# Exclude _id field from projection
data_from_mongo = collection.find({}, {'_id': 0})

# Convert MongoDB cursor to DataFrame
df_from_mongo = pd.DataFrame(data_from_mongo)

# Retrieve _id separately
ids = [str(item['_id']) for item in collection.find({}, {'_id': 1})]

# Add _id field as the first column
df_from_mongo.insert(0, '_id', ids)

# Save DataFrame to CSV
df_from_mongo.to_csv('audio_features_from_mongo.csv', index=False)
