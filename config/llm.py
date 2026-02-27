# llm.py

from langchain_community.chat_models import ChatOllama

def get_llm():
    """
    Returns an Ollama LLM instance.
    Make sure Ollama is running on localhost:11434
    """
    return ChatOllama(
        model="qwen2.5-coder:7b",  # must match ollama list exactly
        base_url="http://localhost:11434",
        temperature=0.7
    )