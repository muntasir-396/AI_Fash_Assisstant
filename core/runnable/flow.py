import json
from services.llm.model import ask_llm
from services.user_memory.memory import update_user_memory


# ==============================
# INTENT EXTRACTION
# ==============================
def extract_intent(user_input: str):

    prompt = f"""
    You are a fashion assistant AI.

    Extract structured information from the user query.

    Return ONLY valid JSON.

    Fields:
    - action (advice | recommend | refine)
    - occasion
    - date
    - style
    - color_preference

    Rules:
    - General question → advice
    - Asking for options → recommend
    - Changing preference → refine

    Example:

    Input: "what should I wear today?"
    Output:
    {{
        "action": "advice",
        "occasion": null,
        "date": null,
        "style": null,
        "color_preference": null
    }}

    Input: "show me outfits"
    Output:
    {{
        "action": "recommend"
    }}

    Input: "I want red"
    Output:
    {{
        "action": "refine",
        "color_preference": "red"
    }}

    Now process:
    "{user_input}"
    """

    response = ask_llm(prompt)

    try:
        data = json.loads(response)
    except:
        data = {}

    return data


# ==============================
# USER INFO EXTRACTION
# ==============================
def extract_user_info(user_input: str):

    prompt = f"""
    Extract user personal attributes from the text.

    Return ONLY valid JSON.

    Fields:
    - height
    - weight
    - preferred_style
    - favorite_color

    Example:
    Input: "I am 5.9 and I like black traditional outfits"
    Output:
    {{
        "height": "5.9",
        "weight": null,
        "preferred_style": "traditional",
        "favorite_color": "black"
    }}

    Now process:
    "{user_input}"
    """

    response = ask_llm(prompt)

    try:
        data = json.loads(response)
    except:
        data = {}

    return data


# ==============================
# MAIN PROCESS INPUT
# ==============================
def process_input(user_input: str):

    cleaned_input = user_input.strip().lower()

    context = extract_intent(cleaned_input)
    user_info = extract_user_info(cleaned_input)

    if user_info:
        update_user_memory(user_info)

    return {
        "text": cleaned_input,
        "context": context,
        "user_info": user_info
    }