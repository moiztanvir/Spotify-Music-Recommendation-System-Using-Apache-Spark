import librosa
import os
import numpy as np
import warnings
warnings.filterwarnings("ignore")
from pymongo import MongoClient
import pandas as pd 

client = MongoClient('mongodb://localhost:27017/')
db = client['music_database']
collection = db['audio_features']

def feature_extraction(name):
    try:
        a_d, s_r = librosa.load(name, sr=22000)
        if len(a_d) == 0:
            print("Empty file:", name)
            return None
        mfcc = librosa.feature.mfcc(y=a_d, sr=s_r, n_mfcc=15)
        sc = librosa.feature.spectral_centroid(y=a_d, sr=s_r)
        zcr = librosa.feature.zero_crossing_rate(a_d)
        feature = np.concatenate((np.mean(mfcc.T, axis=0), np.mean(sc, axis=1), np.mean(zcr, axis=1)))
        return feature
    except Exception as e:
        return None

def convert_str_to_list(df, column_name):
    df[column_name] = df[column_name].apply(lambda x: eval(x) if isinstance(x, str) else [])
    return df

def extract_track_id(filename):
    track_id = filename.split('.')[0]
    track_id = track_id.lstrip('0')
    return int(track_id)

df = pd.read_csv('main.csv')
df = convert_str_to_list(df, 'genres_all')
df1 = df['track_id']
df2 = df['genres_all']
df3 = df['track_title']

with open('checksums.txt', 'a') as file:
    for i in os.listdir(r"fma_large"):
        if os.path.isdir(os.path.join("fma_large", i)):
            for j in os.listdir(os.path.join("fma_large", i)):
                if j.endswith(".mp3"):
                    saim = os.path.join("fma_large", i, j)
                    e_f = feature_extraction(saim)
                    if e_f is not None:
                        track_id = extract_track_id(j)
                        if track_id in df1.values:
                            matching_row = df[df['track_id'] == track_id]
                            genres_all = matching_row['genres_all'].iloc[0]
                            track_title = matching_row['track_title'].iloc[0]
                        else:
                            genres_all = np.nan
                            track_title = np.nan
                        file.write(f"{j[:-4]},{saim},{track_title}\n")
                        temp_feature = [genres_all[0]] + e_f.tolist() if genres_all else [0] + e_f.tolist()
                        temp = {
                            'id': j,
                            'track_title': track_title,
                            'feature':temp_feature
                        }
                        collection.insert_one(temp)

