from services.llm.model import ask_llm


def generate_response(context, recommendations):
    """
    Convert structured data into human-like fashion advice
    """

    prompt = f"""
    You are a professional fashion stylist.

    User context:
    {context}

    Recommended outfits:
    {recommendations}

    Speak naturally like a human.

    Explain:
    - What they should wear
    - Why it suits them
    - Keep it short and friendly
    """

    return ask_llm(prompt)