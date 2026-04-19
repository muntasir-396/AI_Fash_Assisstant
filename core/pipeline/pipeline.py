# ==============================
# MAIN PIPELINE CONTROLLER (CLEAN + FIXED)
# ==============================

from core.runnable.flow import process_input
from services.recommendation.recommender import recommend_outfit
from services.llm.model import ask_llm


# ------------------------------
# Generate human-like AI reply
# ------------------------------
def generate_reply(context, recommendations, chat_history=None):

    # If no products → just give advice
    if not recommendations:
        prompt = f"""
You are a friendly AI fashion stylist.

User Context:
{context}

Give helpful fashion advice (no specific products).
Keep it short and conversational.
"""
        return ask_llm(prompt, chat_history)

    # If products exist → recommend them
    product_text = "\n".join([
        f"- {item['name']} ({item['style']}, {item['color']})"
        for item in recommendations
    ])

    prompt = f"""
You are a smart AI fashion assistant.

User Context:
{context}

Available Products:
{product_text}

Rules:
- ONLY suggest from the list
- Speak naturally like a stylist
- Mention product names clearly
- Keep it short (3-4 lines)

Example tone:
"You’d look great in the Black Panjabi — it’s elegant and perfect for a wedding."

Now respond:
"""
    return ask_llm(prompt, chat_history)


# ------------------------------
# MAIN PIPELINE FUNCTION
# ------------------------------
def run_pipeline(user_input: str, chat_history=None):

    # ------------------------------
    # Step 1: Process input
    # ------------------------------
    processed = process_input(user_input)

    context = processed.get("context", {})
    user_info = processed.get("user_info", {})

    action = context.get("action") or "advice"

    # ------------------------------
    # 🔥 FORCE RECOMMEND LOGIC (IMPORTANT)
    # ------------------------------
    text = user_input.lower()

    if any(word in text for word in [
        "suggest", "show", "recommend", "outfit", "wear", "panjabi", "shirt"
    ]):
        action = "recommend"

    # ------------------------------
    # Step 2: Recommendation logic
    # ------------------------------
    recommendations = []

    if action in ["recommend", "refine"]:
        recommendations = recommend_outfit(user_info, context)

    # ------------------------------
    # Step 3: Generate reply
    # ------------------------------
    assistant_reply = generate_reply(context, recommendations, chat_history)

    # ------------------------------
    # DEBUG (optional but useful)
    # ------------------------------
    print("ACTION:", action)
    print("CONTEXT:", context)
    print("RECOMMENDATIONS:", len(recommendations))

    # ------------------------------
    # Step 4: Return
    # ------------------------------
    return {
        "input": user_input,
        "context": context,
        "action": action,
        "recommendations": recommendations,
        "assistant_reply": assistant_reply
    }