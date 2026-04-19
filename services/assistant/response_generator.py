from services.llm.model import ask_llm

def generate_response(context, recommendations):
    """
    Tuned to behave like a stylist who understands color coordination.
    """
    color = context.get("color_preference", "this")
    
    prompt = f"""
    You are a professional fashion stylist.
    User is interested in: {color} outfits.
    
    Recommended products: {[r['name'] for r in recommendations]}

    Speak like a human stylist.
    - If they asked for white, explain why white is a great choice (e.g., "clean," "elegant," "perfect for summer/weddings").
    - Mention the specific products found.
    - Suggest what they could pair these with (e.g., "tan loafers" or "silver watch").
    - Keep it under 4 lines.
    """

    return ask_llm(prompt)