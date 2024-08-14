import os
import torch
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
import pickle
import gc

# Load CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Function to preprocess images
def preprocess_image(image_path):
    try:
        image = Image.open(image_path).convert("RGB")
        return processor(images=image, return_tensors="pt")["pixel_values"].squeeze(0)
    except Exception as e:
        print(f"Error processing image {image_path}: {e}")
        return None

# Function to encode images with batch processing
def encode_images(image_paths, batch_size=32):
    encoded_images = []
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i+batch_size]
        batch_images = [preprocess_image(path) for path in batch_paths if preprocess_image(path) is not None]
        if batch_images:
            batch_tensor = torch.stack(batch_images)
            with torch.no_grad():
                batch_features = model.get_image_features(batch_tensor)
            encoded_images.append(batch_features)
        
        # Force garbage collection after each batch
        gc.collect()
    
    return torch.cat(encoded_images) if encoded_images else None

# Function to encode text
def encode_text(text):
    inputs = processor(text=text, return_tensors="pt", padding=True)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
    return text_features

# Function to pre-embed images and save embeddings
def pre_embed_images(image_folder, embeddings_file='image_embeddings.pkl', batch_size=32):
    print(f"Starting pre-embedding process for {image_folder}")
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    print(f"Pre-embedding {len(image_paths)} images...")
    encoded_images = encode_images(image_paths, batch_size)
    
    embeddings_data = {
        'embeddings': encoded_images,
        'image_paths': image_paths
    }
    
    with open(embeddings_file, 'wb') as f:
        pickle.dump(embeddings_data, f)
    
    print(f"Embeddings saved to {embeddings_file}")

# Function to load pre-computed embeddings
def load_embeddings(embeddings_file='image_embeddings.pkl'):
    with open(embeddings_file, 'rb') as f:
        embeddings_data = pickle.load(f)
    return embeddings_data['embeddings'], embeddings_data['image_paths']

# Function to find similar images using pre-computed embeddings
def find_similar_images(query_text, encoded_images, image_paths, top_k=10):
    encoded_text = encode_text(query_text)
    
    similarity_scores = torch.nn.functional.cosine_similarity(encoded_text, encoded_images)
    
    top_k_indices = similarity_scores.argsort(descending=True)[:top_k]
    top_k_scores = similarity_scores[top_k_indices]
    
    return [(image_paths[i], score.item()) for i, score in zip(top_k_indices, top_k_scores)]


def get_similar_images(query_text, image_folder, top_k=20, embeddings_file='image_embeddings.pkl'):
    if not os.path.exists(embeddings_file):
        print(f"Embeddings file not found. Creating new embeddings...")
        pre_embed_images(image_folder, embeddings_file)
    
    encoded_images, image_paths = load_embeddings(embeddings_file)
    similar_images = find_similar_images(query_text, encoded_images, image_paths, top_k)
    return [{'path': os.path.basename(path), 'score': score} for path, score in similar_images]

# Optional: Generator-based approach for very large datasets
def encode_images_generator(image_paths, batch_size=32):
    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i+batch_size]
        batch_images = [preprocess_image(path) for path in batch_paths if preprocess_image(path) is not None]
        if batch_images:
            batch_tensor = torch.stack(batch_images)
            with torch.no_grad():
                batch_features = model.get_image_features(batch_tensor)
            yield batch_features
        gc.collect()

# Usage example for generator-based approach:
# encoded_images = torch.cat(list(encode_images_generator(image_paths)))