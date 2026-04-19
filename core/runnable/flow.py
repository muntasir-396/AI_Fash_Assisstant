# ==============================
# NLP EXTRACTION FLOW
# ==============================
import json
import re
from services.llm.model import ask_llm

def clean_json(text):
    """Safely extracts JSON from LLM markdown output."""
    if not text:
        return "{}"
    # Find anything between curly braces to ignore conversational fluff
    match = re.search(r'\{.*\}', text.replace('\n', ''))
    if match:
        return match.group(0)
    # Fallback strip markdown backticks
    text = re.sub(r'```json', '', text, flags=re.IGNORECASE)
    text = re.sub(r'```', '', text)
    return text.strip()

def extract_intent(user_input):
    """Extracts context and intent from user input."""
    prompt = f"""
    Extract fashion intent from this input: "{user_input}"
    Return ONLY a valid JSON object with these keys:
    - "occasion": (e.g., "wedding", "casual", "party", or null)
    - "style": (e.g., "traditional", "modern", "formal", or null)
    - "color_preference": (e.g., "black", "red", or null)
    - "action": (e.g., "recommend", "advice", "refine")
    """
    response = ask_llm(prompt)
    try:
        cleaned_response = clean_json(response)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"⚠️ Intent Parsing Error: {e}")
        return {}

def extract_intent(user_input):
    """Extracts context and intent from user input."""
    prompt = f"""
    Extract fashion intent from this input: "{user_input}"
    Return ONLY a valid JSON object with these keys:
    - "occasion": (e.g., "wedding", "casual", "office", or null)
    - "category": (e.g., "shirt", "panjabi", "suit", or null)
    - "color_preference": (e.g., "white", "black", or null)
    - "specificity_score": (Rate 1 to 5. 1=very vague "I want clothes", 5=highly specific "White linen casual shirt for beach")
    - "action": (e.g., "recommend", "advice", "refine")
    """
    response = ask_llm(prompt)
    try:
        cleaned_response = clean_json(response)
        return json.loads(cleaned_response)
    except Exception as e:
        print(f"⚠️ User Info Parsing Error: {e}")
        return {}

def process_input(user_input):
    """Main entry point for processing text."""
    return {
        "context": extract_intent(user_input),
        "user_info": extract_intent(user_input)
    }