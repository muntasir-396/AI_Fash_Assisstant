import json
import torch
import clip
from PIL import Image
import os

# Load CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)


def get_embedding(image_path):
    image = preprocess(Image.open(image_path)).unsqueeze(0).to(device)

    with torch.no_grad():
        emb = model.encode_image(image)

    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy()[0].tolist()


# Load products
with open("data/products.json", "r") as f:
    products = json.load(f)


# Generate embeddings
for p in products:
    image_path = p["image"]

    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        continue

    print(f"Processing {p['name']}...")
    p["embedding"] = get_embedding(image_path)


# Save new file
with open("data/products_with_embeddings.json", "w") as f:
    json.dump(products, f)

print("✅ Embeddings saved!")