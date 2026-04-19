#AI should remember:-height,weight,preferred style
# ==============================
# USER MEMORY SYSTEM
# ==============================

import json
import os

# Path where we store user data
MEMORY_PATH = "db/user_memory/memory.json"


def load_memory():
    """
    Load stored user memory from file

    If file doesn't exist → create empty memory
    """

    # Check if memory file exists
    if not os.path.exists(MEMORY_PATH):
        return {}

    # Read JSON data
    with open(MEMORY_PATH, "r") as f:
        return json.load(f)


def save_memory(data):
    """
    Save user memory to file
    """

    # Ensure folder exists
    os.makedirs("db/user_memory", exist_ok=True)

    # Write JSON
    with open(MEMORY_PATH, "w") as f:
        json.dump(data, f, indent=4)


def update_user_memory(new_data):
    """
    Update memory with new user info

    Example:
    new_data = {
        "height": "5.8",
        "style": "traditional"
    }
    """

    memory = load_memory()

    # Merge new data into memory
    memory.update(new_data)

    save_memory(memory)

    return memory


def get_user_memory():
    """
    Get current stored user preferences
    """

    return load_memory()