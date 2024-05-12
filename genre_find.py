import pandas as pd

def filter_columns(input_file, output_file, selected_columns):
    df = pd.read_csv(input_file)
    
    # Convert 'track_id' column to string type and check if it contains only digits
    df = df[df['track_id'].astype(str).str.isdigit()]
    
    df_filtered = df[selected_columns]
    df_filtered.to_csv(output_file, index=False)

input_file = 'Tracks.csv'
output_file = 'main.csv'
selected_columns = ['track_id', 'genres_all', 'track_title']

filter_columns(input_file, output_file, selected_columns)
