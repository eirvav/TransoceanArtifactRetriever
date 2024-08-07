import os
import shutil
import json
import tempfile
from flask import Flask, render_template, request, jsonify, send_file
from clip_image_retrieval import get_similar_images

app = Flask(__name__)

IMAGE_FOLDER = os.path.join(app.static_folder, 'images')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = get_similar_images(query, IMAGE_FOLDER)
    return jsonify(results)

@app.route('/download', methods=['POST'])
def download_images():
    selected_images = request.form.get('images')
    if not selected_images:
        return "No images selected", 400

    selected_images = json.loads(selected_images)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        download_folder = os.path.join(temp_dir, 'selected_images')
        os.makedirs(download_folder)
        
        for img_name in selected_images:
            src_path = os.path.join(IMAGE_FOLDER, img_name)
            dst_path = os.path.join(download_folder, img_name)
            shutil.copy2(src_path, dst_path)
        
        zip_path = shutil.make_archive(download_folder, 'zip', download_folder)
        return send_file(zip_path, as_attachment=True, download_name='selected_images.zip')

if __name__ == '__main__':
    app.run(debug=True)