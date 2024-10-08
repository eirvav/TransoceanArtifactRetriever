import os
import io
import json
import zipfile
from flask import Flask, render_template, request, jsonify, send_file
from clip_image_retrieval import get_similar_images, pre_embed_images

app = Flask(__name__)

IMAGE_FOLDER = os.path.join(app.static_folder, 'images')
EMBEDDINGS_FILE = 'image_embeddings.pkl'

def embed_images_if_needed():
    if not os.path.exists(EMBEDDINGS_FILE):
        embed_choice = input("Embeddings file not found. Do you want to embed the images? (y/n): ").lower()
        if embed_choice == 'y':
            print("Embedding images...")
            pre_embed_images(IMAGE_FOLDER, EMBEDDINGS_FILE)
            print("Embedding complete.")
        else:
            print("Skipping image embedding. Note that embedding will be done on the first search request.")
    else:
        print("Embeddings file found. Using existing embeddings.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    results = get_similar_images(query, IMAGE_FOLDER, embeddings_file=EMBEDDINGS_FILE)
    return jsonify(results)

@app.route('/download', methods=['POST'])
def download_images():
    selected_images = request.form.get('images')
    if not selected_images:
        return "No images selected", 400

    selected_images = json.loads(selected_images)
    
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for img_name in selected_images:
            img_path = os.path.join(IMAGE_FOLDER, img_name)
            if os.path.exists(img_path):
                zf.write(img_path, img_name)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='selected_images.zip'
    )

if __name__ == '__main__':
    embed_images_if_needed()
    app.run(debug=True, port=5001)  # or any other port number