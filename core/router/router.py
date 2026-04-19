#This is your brain switch
#Without this:
#system doesn’t know what function to call 


# ==============================
# ROUTER (INTENT DECISION)
# ==============================

def route_decision(user_input):
    """
    Decide what user wants

    Returns:
        "recommend" → outfit suggestion
        "unknown" → fallback
    """

    text = user_input.lower()

    # If user asks about clothing
    if "wear" in text or "outfit" in text:
        return "recommend"

    return "unknown"
