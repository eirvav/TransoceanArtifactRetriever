import os
import torch
from PIL import Image
import numpy as np
from transformers import CLIPProcessor, CLIPModel

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

# Function to find similar images
def find_similar_images(query_text, image_paths, top_k=10):
    # Encode images
    encoded_images = encode_images(image_paths)
    if encoded_images is None:
        print("No valid images found.")
        return []
    
    # Encode text query
    encoded_text = encode_text(query_text)
    
    # Calculate similarity scores
    similarity_scores = torch.nn.functional.cosine_similarity(encoded_text, encoded_images)
    
    # Get top-k similar images
    top_k_indices = similarity_scores.argsort(descending=True)[:top_k]
    top_k_scores = similarity_scores[top_k_indices]
    
    return [(image_paths[i], score.item()) for i, score in zip(top_k_indices, top_k_scores)]

# Example usage
if __name__ == "__main__":
    # Replace this with the path to your image folder
    image_folder = "/Users/eirvav/clip_image_retrieval/fridgeObjects/can"
    
    # Get all image files from the folder
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    if not image_paths:
        print(f"No image files found in {image_folder}")
    else:
        print(f"Found {len(image_paths)} images in {image_folder}")
        
        query_text = "a blue soda can"
        similar_images = find_similar_images(query_text, image_paths)
        
        print(f"\nTop 5 images similar to '{query_text}':")
        for path, score in similar_images:
            print(f"Image: {path}, Similarity Score: {score:.4f}")

def get_similar_images(query_text, image_folder, top_k=15):
    image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) 
                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
    
    similar_images = find_similar_images(query_text, image_paths, top_k)
    return [{'path': os.path.basename(path), 'score': score} for path, score in similar_images]