from flask import Flask, render_template, send_from_directory, request, jsonify

app = Flask(__name__)
downloads_path = None

@app.route('/')
def index():
    global downloads_path
    with open('similar.txt', 'r') as file:
        similar_song_ids = file.readlines()
        first_song_id = similar_song_ids[0].strip()
        first_song_id = similar_song_ids[0][0:6]
    similar_song_title1 = []
    similar_song_title2 = []
    for i in range(len(similar_song_ids)):
        temp = similar_song_ids[i][0:6]
        similar_song_title1.append(temp)
        similar_song_title2.append('-')
    
    with open('checksums.txt', 'r') as file:
        checksums = file.readlines()
        for line in checksums:
            s_path = line.strip()
            song_id = s_path[0:6]
            if song_id in similar_song_title1:
                index = similar_song_title1.index(song_id)
                similar_song_title2[index] = s_path[33:]
    
    with open('checksums.txt', 'r') as file:
        checksums = file.readlines()
        for line in checksums:
            s_path = line.strip()
            song_id = s_path[0:6]
            if song_id == first_song_id:
                s_path = s_path[7:31]
                file_path = s_path
                downloads_path = file_path[0:13]
                zipped_data = zip(similar_song_ids, similar_song_title2)
                return render_template('index.html', file_path=file_path, zipped_data=zipped_data)

        return "Song path not found"

@app.route('/audio/<path:filename>')
def download_file(filename):
    global downloads_path
    return send_from_directory(downloads_path, filename)

@app.route('/store_id', methods=['POST'])
def store_id():
    data = request.json
    song_id = data.get('songID')
    with open('music.txt', 'a') as file:
        file.write(song_id + '\n')
    return jsonify({'message': 'Song ID stored successfully'})

if __name__ == '__main__':
    app.run(debug=True)

