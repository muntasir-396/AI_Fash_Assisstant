#With this:
#clean readable output for UI

# ==============================
# RESPONSE BUILDER
# ==============================

def build_response(results):
    """
    Convert raw results into user-friendly output

    results: list of product dictionaries
    """

    # If no products found
    if not results:
        return {
            "text": "No recommendation found",
            "images": []
        }

    # Create response text
    text = "Recommended outfits:\n"

    # Store image paths
    images = []

    # Loop through products
    for item in results:
        # Add product name to text
        text += f"- {item['name']}\n"

        # Collect image path
        images.append(item["image"])

    # Return structured response
    return {
        "text": text,
        "images": images
    }
