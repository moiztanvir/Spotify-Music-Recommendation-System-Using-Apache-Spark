import subprocess
import time

def run_python_script(script_name):
    subprocess.run(["/usr/bin/python3", script_name])

def upload_to_mongodb():
    subprocess.run([
        "mongoimport",
        "--host",
        "localhost",
        "--db",
        "music2_database",
        "--collection",
        "music2_collection",
        "--type",
        "csv",
        "--file",
        "audio_features_from_mongo.csv",
        "--headerline"
    ])

if __name__ == "__main__":
    run_python_script("genre_find.py")

    run_python_script("Project.py")

    run_python_script("change.py")

    upload_to_mongodb()
    
    subprocess.run(["gnome-terminal", "--", "bash", "-c", "cd /home/hdoop/kafka; bin/zookeeper-server-start.sh config/zookeeper.properties; exec bash"])
    
    subprocess.run(["gnome-terminal", "--", "bash", "-c", "cd /home/hdoop/kafka; bin/kafka-server-start.sh config/server.properties; exec bash"])
    
    time.sleep(5)
    subprocess.run(["gnome-terminal", "--", "bash", "-c", "cd /home/hdoop/BIG_DATA_PROJECT;python3 producer.py;exec bash"])
    
    time.sleep(5)
    subprocess.run(["gnome-terminal", "--", "bash", "-c", "cd /home/hdoop/BIG_DATA_PROJECT;python3 consumer.py;exec bash"])
    
    time.sleep(10)
    subprocess.run(["gnome-terminal", "--", "bash", "-c", "cd /home/hdoop/BIG_DATA_PROJECT;python3 web_app.py;exec bash"])
