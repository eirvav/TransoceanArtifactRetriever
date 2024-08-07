from flask import Flask, render_template, request, jsonify, send_file
from flask_caching import Cache
from clip_image_retrieval import get_similar_images, get_image_from_cifar100
import io
import threading

app = Flask(__name__)
app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)

# Global variable to store background task results
background_tasks = {}

@app.route('/')
def index():
    return render_template('index.html')

def background_search(query, task_id):
    results = get_similar_images(query)
    background_tasks[task_id] = {'state': 'SUCCESS', 'result': results}

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    task_id = f"task_{len(background_tasks)}"
    background_tasks[task_id] = {'state': 'PENDING'}
    thread = threading.Thread(target=background_search, args=(query, task_id))
    thread.start()
    return jsonify({"task_id": task_id}), 202

@app.route('/status/<task_id>')
def task_status(task_id):
    task = background_tasks.get(task_id, {})
    if task.get('state') == 'PENDING':
        response = {
            'state': 'PENDING',
            'status': 'Processing...'
        }
    elif task.get('state') == 'SUCCESS':
        response = {
            'state': 'SUCCESS',
            'result': task['result']
        }
    else:
        response = {
            'state': 'FAILURE',
            'status': 'Task failed or not found'
        }
    return jsonify(response)

@app.route('/image/<path:filename>')
@cache.memoize(50)
def serve_image(filename):
    if filename.startswith('cifar100_'):
        index = int(filename.split('_')[1])
        img = get_image_from_cifar100(index)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')

@app.route('/download', methods=['POST'])
def download_images():
    selected_images = request.form.getlist('images[]')
    if not selected_images:
        return "No images selected", 400

    import zipfile
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for img_name in selected_images:
            if img_name.startswith('cifar100_'):
                index = int(img_name.split('_')[1])
                img = get_image_from_cifar100(index)
                img_io = io.BytesIO()
                img.save(img_io, 'PNG')
                img_io.seek(0)
                zf.writestr(f"{img_name}.png", img_io.getvalue())

    memory_file.seek(0)
    return send_file(memory_file, mimetype='application/zip', as_attachment=True, download_name='selected_images.zip')

if __name__ == '__main__':
    app.run(debug=True)