# ==============================
# LLM WRAPPER (LangChain + Mistral)
# ==============================

import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

# Load API keys from .env
load_dotenv()

# Initialize model
llm = ChatMistralAI(
    model="mistral-small-latest",
    temperature=0
)

def ask_llm(prompt, chat_history=None):

    messages = []

    # Add chat history if exists
    if chat_history:
        for msg in chat_history:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

    # Add current prompt
    messages.append({
        "role": "user",
        "content": prompt
    })

    # Call model
    response = llm.invoke(messages)

    return response.content