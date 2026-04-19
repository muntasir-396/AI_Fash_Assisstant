# ==============================
# PERSONALIZED RECOMMENDER (FINAL FIXED)
# ==============================

import json
import math
import random
import torch
import clip
from services.user_memory.memory import get_user_memory


# ------------------------------
# LOAD CLIP MODEL
# ------------------------------
device = "cpu"
clip_model, _ = clip.load("ViT-B/32", device=device)


# ------------------------------
# TEXT → EMBEDDING
# ------------------------------
def get_text_embedding(text):
    tokens = clip.tokenize([text]).to(device)

    with torch.no_grad():
        emb = clip_model.encode_text(tokens)

    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy()[0].tolist()


# ------------------------------
# LOAD PRODUCTS
# ------------------------------
def load_products():
    with open("data/products.json", "r") as f:
        return json.load(f)


# ------------------------------
# COSINE SIMILARITY
# ------------------------------
def cosine_similarity(vec1, vec2):
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0

    return dot / (norm1 * norm2)


# ------------------------------
# SCORE (SMART)
# ------------------------------
def score_product(product, context, memory):
    score = 0

    # strong signals
    if context.get("occasion") == product["category"]:
        score += 5

    if context.get("style") == product["style"]:
        score += 4

    if context.get("color_preference") == product["color"]:
        score += 3

    # memory
    if memory.get("preferred_style") == product["style"]:
        score += 2

    if memory.get("favorite_color") == product["color"]:
        score += 2

    return score


# ------------------------------
# DIVERSITY
# ------------------------------
def diversify(products):
    seen = set()
    result = []

    for p in products:
        key = (p["category"], p["style"])

        if key not in seen:
            result.append(p)
            seen.add(key)

        if len(result) >= 3:
            break

    return result


# ------------------------------
# MAIN RECOMMENDER
# ------------------------------
def recommend_outfit(user_info, context):

    products = load_products()
    memory = get_user_memory()

    # 🔥 USE FULL USER INPUT (VERY IMPORTANT)
    query_text = context.get("raw_input", "")

    if not query_text:
        query_text = f"{context.get('occasion','')} {context.get('style','')}"

    query_embedding = get_text_embedding(query_text)

    scored = []

    for p in products:
        score = score_product(p, context, memory)

        # 🔥 USE EMBEDDING DIRECTLY FROM PRODUCT
        if "embedding" in p:
            sim = cosine_similarity(query_embedding, p["embedding"])
            score += sim * 3

        # 🔥 ADD RANDOMNESS (avoid same result)
        score += random.uniform(0, 0.5)

        scored.append((p, score))

    # sort
    scored.sort(key=lambda x: x[1], reverse=True)

    ranked = [item[0] for item in scored]

    # diversity
    final = diversify(ranked)

    return final