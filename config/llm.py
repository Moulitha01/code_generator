import os
from langchain_ollama import ChatOllama

def get_llm(temperature=0.4):
    return ChatOllama(
        model="qwen2.5-coder:7b",
        base_url=os.getenv(
            "OLLAMA_BASE_URL",
            "http://localhost:11434"
        ),
        temperature=temperature
    )