import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from core.pipeline.pipeline import run_pipeline


# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(page_title="AI Fashion Assistant", layout="centered")

st.title("AI Fashion Assistant 👕")
st.caption("Ask anything like: wedding outfit, casual look, party style...")


# ==============================
# INIT CHAT MEMORY
# ==============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


# ==============================
# SHOW CHAT HISTORY (🔥 FIXED)
# ==============================
for msg in st.session_state.chat_history:

    with st.chat_message(msg["role"]):

        # show text
        st.write(msg["content"])

        # 🔥 show images INSIDE message
        if msg.get("products"):
            cols = st.columns(len(msg["products"]))

            for i, item in enumerate(msg["products"]):
                with cols[i]:
                    st.image(item["image"], use_container_width=True)
                    st.caption(item["name"])


# ==============================
# USER INPUT
# ==============================
user_input = st.chat_input("Ask your fashion assistant...")


# ==============================
# MAIN LOGIC
# ==============================
if user_input:

    # show user msg
    with st.chat_message("user"):
        st.write(user_input)

    # save user msg
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })

    try:
        # limit history
        chat_history = st.session_state.chat_history[-6:]

        with st.spinner("Thinking..."):
            result = run_pipeline(user_input, chat_history=chat_history)

        reply = result.get("assistant_reply", "")
        products = result.get("recommendations", [])

        # 🔥 show assistant message + products TOGETHER
        with st.chat_message("assistant"):
            st.write(reply)

            if products:
                cols = st.columns(len(products))

                for i, item in enumerate(products):
                    with cols[i]:
                        st.image(item["image"], use_container_width=True)
                        st.caption(item["name"])

        # 🔥 save BOTH text + products
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": reply,
            "products": products
        })

    except Exception as e:
        st.error(f"Error: {e}")