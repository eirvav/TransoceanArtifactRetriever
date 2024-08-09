import os
import torch
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel
import pickle

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

# Function to encode images
def encode_images(image_paths):
    encoded_images = []
    for image_path in image_paths:
        preprocessed_image = preprocess_image(image_path)
        if preprocessed_image is not None:
            with torch.no_grad():
                image_features = model.get_image_features(preprocessed_image.unsqueeze(0))
            encoded_images.append(image_features)
    return torch.cat(encoded_images) if encoded_images else None

# Function to encode text
def encode_text(text):
    inputs = processor(text=text, return_tensors="pt", padding=True)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
    return text_features

# Function to pre-embed images and save embeddings
def pre_embed_images(image_folder, embeddings_file='image_embeddings.pkl'):
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    print(f"Pre-embedding {len(image_paths)} images...")
    encoded_images = encode_images(image_paths)
    
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

# Modified get_similar_images function to use pre-computed embeddings
def get_similar_images(query_text, image_folder, top_k=20, embeddings_file='image_embeddings.pkl'):
    if not os.path.exists(embeddings_file):
        pre_embed_images(image_folder, embeddings_file)
    
    encoded_images, image_paths = load_embeddings(embeddings_file)
    similar_images = find_similar_images(query_text, encoded_images, image_paths, top_k)
    return [{'path': os.path.basename(path), 'score': score} for path, score in similar_images]