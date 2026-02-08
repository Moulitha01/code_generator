"""
LLM Configuration Module
Provides Gemini model configuration for all agents
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_gemini_llm(temperature: float = 0.7):
    """
    Get configured Gemini LLM instance.
    
    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
        
    Returns:
        ChatGoogleGenerativeAI instance
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY not found! "
            "Please set it in .env file or as environment variable."
        )
    
    return ChatGoogleGenerativeAI(
        model="gemini-3-flash-preview",
        google_api_key=api_key,
        temperature=temperature
    )


def verify_api_key():
    """
    Verify that API key is configured.
    
    Returns:
        bool: True if API key exists, False otherwise
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    return api_key is not None and len(api_key) > 0