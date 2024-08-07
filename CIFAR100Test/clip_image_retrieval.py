import torch
from torchvision import datasets, transforms
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np
import os
import pickle

# Load CLIP model and processor
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# Load CIFAR100 dataset
transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Lambda(lambda x: x.repeat(3, 1, 1) if x.size(0)==1 else x)
])
cifar100 = datasets.CIFAR100(root='./data', download=True, train=False, transform=transform)

# File to store pre-computed embeddings
EMBEDDINGS_FILE = 'cifar100_embeddings.pkl'

def encode_image(img):
    inputs = processor(images=img, return_tensors="pt", padding=True)
    with torch.no_grad():
        image_features = model.get_image_features(**inputs)
    return image_features

def encode_text(text):
    inputs = processor(text=text, return_tensors="pt", padding=True)
    with torch.no_grad():
        text_features = model.get_text_features(**inputs)
    return text_features

def precompute_embeddings():
    if os.path.exists(EMBEDDINGS_FILE):
        print("Loading pre-computed embeddings...")
        with open(EMBEDDINGS_FILE, 'rb') as f:
            return pickle.load(f)
    
    print("Computing embeddings for all images...")
    embeddings = []
    for i, (img, _) in enumerate(cifar100):
        img = transforms.ToPILImage()(img)
        embedding = encode_image(img)
        embeddings.append(embedding)
        if i % 1000 == 0:
            print(f"Processed {i} images")
    
    embeddings = torch.cat(embeddings)
    
    print("Saving embeddings...")
    with open(EMBEDDINGS_FILE, 'wb') as f:
        pickle.dump(embeddings, f)
    
    return embeddings

# Pre-compute embeddings
image_embeddings = precompute_embeddings()

def find_similar_images(query_text, top_k=5):
    encoded_text = encode_text(query_text)
    
    similarity_scores = torch.nn.functional.cosine_similarity(encoded_text, image_embeddings)
    top_k_indices = similarity_scores.argsort(descending=True)[:top_k]
    top_k_scores = similarity_scores[top_k_indices]
    
    return [(idx.item(), score.item()) for idx, score in zip(top_k_indices, top_k_scores)]

def get_image_from_cifar100(index):
    img, _ = cifar100[index]
    return transforms.ToPILImage()(img)

def get_similar_images(query_text, top_k=15):
    similar_images = find_similar_images(query_text, top_k)
    return [{'path': f'cifar100_{idx}', 'score': score} for idx, score in similar_images]