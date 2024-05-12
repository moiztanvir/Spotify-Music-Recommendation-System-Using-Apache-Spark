from kafka import KafkaProducer
import json
import time

def read_ids_from_file(filename):
    with open(filename) as file:
        return [line.strip() for line in file]

def main():
    producer = KafkaProducer(bootstrap_servers='localhost:9092',
                             value_serializer=lambda x: json.dumps(x).encode('utf-8'))

    sent_ids = set()
    last_position = 0

    while True:
        with open("music.txt") as file:
            file.seek(last_position)

            for line in file:
                track_id = line.strip()

                if not track_id:
                    continue

                producer.send('similar-songs-topic', value=track_id)
                print("Sent ID:", track_id)
                
                sent_ids.add(track_id)

            last_position = file.tell()

        if last_position == 0:
            sent_ids.clear()

    producer.close()

if __name__ == "__main__":
    main()
