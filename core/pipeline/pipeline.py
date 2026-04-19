# ==============================
# MAIN PIPELINE CONTROLLER (THE BRAIN)
# ==============================

from core.runnable.flow import process_input
from core.router.router import route_decision
from services.recommendation.recommender import recommend_outfit
from services.assistant.response_generator import generate_response
from services.llm.model import ask_llm

def run_pipeline(user_input: str, chat_history=None):
    """
    The main brain of the AI Stylist. 
    Flow: Understand -> Route -> Specificity Check -> Retrieve -> Respond
    """

    # ------------------------------
    # Step 1: Process input & Extract Intent
    # ------------------------------
    processed = process_input(user_input)
    context = processed.get("context", {})
    user_info = processed.get("user_info", {})
    
    # Store the raw input so the recommender can use it for CLIP embeddings
    context["raw_input"] = user_input

    # ------------------------------
    # Step 2: Route the Decision
    # ------------------------------
    # We ask the router what the user actually wants
    action = route_decision(user_input)
    
    # Fallback to the NLP extracted action if the router is uncertain
    if action == "unknown":
        action = context.get("action", "advice")

    # ------------------------------
    # Step 3: Specificity Check (The Clarification Loop)
    # ------------------------------
    # Default to 5 (specific) if the LLM didn't return a score
    specificity = context.get("specificity_score", 5)
    occasion = context.get("occasion")
    style = context.get("style")
    
    # Force clarification if the score is low OR if they didn't specify an occasion/style
    # This prevents showing 100 random shirts when the user is too vague.
    if action == "recommend":
        if specificity < 4 or not occasion or not style:
            action = "clarify"

    # ------------------------------
    # Step 4: Recommendation Logic
    # ------------------------------
    recommendations = []

    if action in ["recommend", "refine"]:
        # Only trigger the heavy recommender engine if the user was specific enough
        recommendations = recommend_outfit(user_info, context)

    # ------------------------------
    # Step 5: Generate Human-Like Reply
    # ------------------------------
    if action == "clarify":
        # Do NOT show products yet. Ask a friendly multiple-choice question to narrow it down.
        prompt = f"""
        User wants: {context.get('color_preference', 'something')} {context.get('category', 'clothes')}.
        This is too broad for a professional stylist. 
        
        Ask ONE friendly, professional multiple-choice question to narrow down the occasion or style.
        Example: "A white shirt is a classic! Are you looking for something formal for the office, or casual for the weekend?"
        """
        assistant_reply = ask_llm(prompt, chat_history)

    elif not recommendations:
        # Give helpful fashion advice when no specific products are requested or found
        prompt = f"""
        You are Tooly, a friendly and premium AI fashion stylist.
        User Context: {context}
        User Input: "{user_input}"
        
        Give helpful fashion advice. Do NOT list specific products.
        Keep it short, professional, and conversational. Ask a follow-up question to guide them.
        """
        assistant_reply = ask_llm(prompt, chat_history)
        
    else:
        # Use the dedicated response generator for product recommendations
        assistant_reply = generate_response(context, recommendations)

    # ------------------------------
    # DEBUG LOGS (Terminal)
    # ------------------------------
    print(f"🧠 INTENT ACTION: {action}")
    print(f"🎯 SPECIFICITY: {specificity}")
    print(f"📊 CONTEXT: {context}")
    print(f"👕 PRODUCTS FOUND: {len(recommendations)}")

    # ------------------------------
    # Step 6: Return Payload to UI
    # ------------------------------
    return {
        "input": user_input,
        "context": context,
        "action": action,
        "recommendations": recommendations,
        "assistant_reply": assistant_reply
    }