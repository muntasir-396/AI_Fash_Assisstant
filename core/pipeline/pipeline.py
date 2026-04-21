from core.runnable.flow import process_input
from core.router.router import route_decision
from services.recommendation.recommender import recommend_outfit
from services.assistant.response_generator import generate_response
from services.llm.model import ask_llm
from services.user_memory.memory import get_user_memory, update_user_memory

def run_pipeline(user_input: str, chat_history=None):
    """
    Stateful Orchestrator: This is the central hub of your Personal Fashion Assistant.
    It combines past knowledge (Memory) with the current user message.
    """
    # 1. ANALYZE CURRENT MESSAGE
    # We extract intent (color, category, etc.) from the latest input
    processed = process_input(user_input)
    current_intent = processed.get("context", {})
    user_info = processed.get("user_info", {})
    
    # 2. UPDATE PERSONAL MEMORY
    # We save newly discovered info into the session-based memory
    update_user_memory(current_intent)
    
    # 3. GET FULL ACCUMULATED CONTEXT
    # This retrieves everything we know about the user across the whole conversation
    full_context = get_user_memory()
    full_context["raw_input"] = user_input # Keep original text for CLIP similarity

    # 4. DECIDE HIGH-LEVEL ACTION
    # Does the user want a recommendation, general advice, or are they refining a previous pick?
    action = route_decision(user_input)
    if action == "unknown":
        action = current_intent.get("action", "advice")

    # ------------------------------
    # 5. SMART CLARIFICATION LOOP
    # ------------------------------
    recommendations = []
    
    if action == "recommend":
        # We check the FULL context (not just the current message) for missing pieces
        missing = []
        if not full_context.get("occasion"): missing.append("occasion (e.g. wedding, office)")
        if not full_context.get("style"): missing.append("style (e.g. formal, traditional)")
        
        if missing:
            # If we're missing info, we switch to 'clarify' mode
            action = "clarify"
            missing_label = " and ".join(missing)
            
            prompt = f"""
            The user wants fashion help. You already know: {full_context}.
            However, you are still missing the {missing_label}.
            
            As a premium personal stylist, acknowledge what you know and ask a 
            friendly follow-up question to get the missing {missing_label}.
            """
            assistant_reply = ask_llm(prompt, chat_history)
        else:
            # We have everything! occasion, style, and category.
            # Run the recommendation engine using CLIP embeddings
            recommendations = recommend_outfit(user_info, full_context)
            assistant_reply = generate_response(full_context, recommendations)
    
    elif action == "advice":
        # General fashion guidance without product listings
        prompt = f"""
        You are Tooly, an expert stylist. Give professional fashion advice for: "{user_input}".
        Context: {full_context}
        Keep it short, helpful, and ask if they want to see specific product recommendations.
        """
        assistant_reply = ask_llm(prompt, chat_history)
    else:
        # Fallback if the intent is unclear
        assistant_reply = "I'm here to help you look your best! Are you dressing up for a specific event today?"

    # ------------------------------
    # 6. RETURN RESULTS
    # ------------------------------
    return {
        "input": user_input,
        "context": full_context,
        "action": action,
        "recommendations": recommendations,
        "assistant_reply": assistant_reply
    }