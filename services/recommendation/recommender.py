# ==============================
# PERSONALIZED RECOMMENDER (FIXED)
# ==============================

import json
import math
import random
import torch
import clip
import streamlit as st
from services.user_memory.memory import get_user_memory

# ------------------------------
# CACHE CLIP MODEL (Fast Performance)
# ------------------------------
@st.cache_resource
def load_clip_model():
    """Loads the model ONCE and keeps it in memory."""
    device = "cpu"
    model, _ = clip.load("ViT-B/32", device=device)
    return model, device

# ------------------------------
# TEXT → EMBEDDING
# ------------------------------
def get_text_embedding(text):
    clip_model, device = load_clip_model()
    tokens = clip.tokenize([text]).to(device)

    with torch.no_grad():
        emb = clip_model.encode_text(tokens)

    emb = emb / emb.norm(dim=-1, keepdim=True)
    return emb.cpu().numpy()[0].tolist()

# ------------------------------
# LOAD PRODUCTS (With Embeddings!)
# ------------------------------
@st.cache_data
def load_products():
    """Loads the products containing the pre-computed CLIP embeddings."""
    try:
        with open("data/products_with_embeddings.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback if the embedding file is missing for some reason
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
    
    # Safely handle None values from context/memory
    if context.get("occasion") and context.get("occasion") == product.get("category"):
        score += 5
    if context.get("style") and context.get("style") == product.get("style"):
        score += 4
    if context.get("color_preference") and context.get("color_preference") == product.get("color"):
        score += 3
        
    if memory.get("preferred_style") and memory.get("preferred_style") == product.get("style"):
        score += 2
    if memory.get("favorite_color") and memory.get("favorite_color") == product.get("color"):
        score += 2

    return score

# ------------------------------
# DIVERSITY
# ------------------------------
def diversify(products):
    seen = set()
    result = []

    for p in products:
        key = (p.get("category"), p.get("style"))
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

    # 🔥 Fix the "None None" bug by sanitizing strings
    query_text = context.get("raw_input", "").strip()
    
    if not query_text:
        occasion = context.get('occasion') or ""
        style = context.get('style') or ""
        query_text = f"{occasion} {style}".strip()
        
    # If we STILL have no text, just return diverse popular items
    if not query_text:
        return diversify(products)

    query_embedding = get_text_embedding(query_text)
    scored = []

    for p in products:
        score = score_product(p, context, memory)

        # 🔥 Embedding logic will now actually execute!
        if "embedding" in p:
            sim = cosine_similarity(query_embedding, p["embedding"])
            score += sim * 3

        # Add slight randomness for variety
        score += random.uniform(0, 0.5)
        scored.append((p, score))

    scored.sort(key=lambda x: x[1], reverse=True)
    ranked = [item[0] for item in scored]

    return diversify(ranked)