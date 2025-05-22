from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import os
import threading
import uuid
from pytube import YouTube

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(app.static_folder, 'download')
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

progress_data = {}

def download_video(url, format_, task_id):
    try:
        yt = YouTube(url)
        if format_ == 'mp3':
            stream = yt.streams.filter(only_audio=True).first()
            out_file = stream.download(output_path=DOWNLOAD_FOLDER)
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            os.rename(out_file, new_file)
            filename = os.path.basename(new_file)
        else:
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            filename = stream.default_filename
            stream.download(output_path=DOWNLOAD_FOLDER)
        progress_data[task_id] = {'status': 'done', 'filename': filename}
    except Exception as e:
        progress_data[task_id] = {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    format_ = request.form.get('format')
    task_id = str(uuid.uuid4())

    progress_data[task_id] = {'status': 'downloading'}

    thread = threading.Thread(target=download_video, args=(url, format_, task_id))
    thread.start()

    return jsonify({'task_id': task_id})

@app.route('/progress/<task_id>')
def progress(task_id):
    data = progress_data.get(task_id, {'status': 'notfound'})
    return jsonify(data)

@app.route('/downloaded/<path:filename>')
def downloaded(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
