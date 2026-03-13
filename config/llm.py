# llm.py

from langchain_ollama import ChatOllama

def get_llm(temperature=0.4):
    """
    Returns an Ollama LLM instance.
    Make sure Ollama is running on localhost:11434
    """
    return ChatOllama(
        model="qwen2.5-coder:7b",  
        base_url="http://localhost:11434",
        temperature=0.7
    )