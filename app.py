from flask import Flask, render_template, request, jsonify, send_file
import yt_dlp
import uuid
import os

app = Flask(__name__)
downloads = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    format = request.form['format']
    id = str(uuid.uuid4())
    file_path = f"downloads/{id}.%(ext)s"

    ydl_opts = {
        'outtmpl': file_path,
        'format': 'bestaudio/best' if format == 'audio' else 'bestvideo+bestaudio/best',
        'progress_hooks': [lambda d: progress_hook(d, id)],
    }

    info = {}

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        thumbnail = info.get('thumbnail')
        title = info.get('title')

    downloads[id] = {'progress': '0%', 'status': 'downloading', 'filename': None}

    def start_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            info_dict = ydl.extract_info(url, download=False)
            ext = 'm4a' if format == 'audio' else 'mp4'
            downloads[id]['filename'] = f"{id}.{ext}"
            downloads[id]['status'] = 'done'

    import threading
    threading.Thread(target=start_download).start()

    return jsonify({'download_id': id, 'thumbnail': thumbnail, 'title': title})

@app.route('/progress/<id>')
def progress(id):
    return jsonify(downloads.get(id, {}))

@app.route('/get-file/<id>')
def get_file(id):
    filename = downloads[id]['filename']
    return send_file(f"downloads/{filename}", as_attachment=True)

def progress_hook(d, id):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '').strip()
        downloads[id]['progress'] = percent
    elif d['status'] == 'finished':
        downloads[id]['progress'] = '100%'
        downloads[id]['status'] = 'done'

if __name__ == '__main__':
    if not os.path.exists('downloads'):
        os.mkdir('downloads')
    app.run(debug=True)
