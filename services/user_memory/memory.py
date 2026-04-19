# ==============================
# USER MEMORY SYSTEM (FIXED FOR STREAMLIT)
# ==============================

import streamlit as st

def load_memory():
    """
    Load stored user memory from Streamlit session state.
    This ensures User A and User B don't overwrite each other's data.
    """
    if "user_memory" not in st.session_state:
        st.session_state.user_memory = {}
    return st.session_state.user_memory


def save_memory(data):
    """
    Save user memory back to Streamlit session state.
    """
    st.session_state.user_memory = data


def update_user_memory(new_data):
    """
    Update memory with new user info dynamically.

    Example:
    new_data = {
        "height": "5.8",
        "style": "traditional"
    }
    """
    memory = load_memory()

    # Filter out empty or null values so we don't overwrite good data with "None"
    valid_new_data = {k: v for k, v in new_data.items() if v is not None}
    
    # Merge new valid data into memory
    memory.update(valid_new_data)

    save_memory(memory)

    return memory


def get_user_memory():
    """
    Get current stored user preferences for the active session.
    """
    return load_memory()