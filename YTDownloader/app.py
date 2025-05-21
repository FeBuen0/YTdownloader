from flask import Flask, render_template, request, jsonify
from tasks import download_and_merge
from celery.result import AsyncResult

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_download', methods=['POST'])
def start_download():
    url = request.json.get('url')
    if not url:
        return jsonify({'error': 'URL não fornecida'}), 400

    task = download_and_merge.apply_async(args=[url])
    return jsonify({'task_id': task.id})

@app.route('/progress/<task_id>')
def progress(task_id):
    task = AsyncResult(task_id)
    if task.state == 'PENDING':
        # Tarefa ainda não iniciada
        response = {'state': task.state, 'progress': 0, 'status': 'Pendente...'}
    elif task.state != 'FAILURE':
        info = task.info
        if info and 'progress' in info:
            response = {'state': task.state, 'progress': info['progress'], 'status': info.get('status', '')}
        else:
            response = {'state': task.state, 'progress': 0, 'status': ''}
    else:
        # Em caso de erro
        response = {'state': task.state, 'progress': 0, 'status': str(task.info)}

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
