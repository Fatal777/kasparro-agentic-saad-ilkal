"""
Multi-Provider LLM Factory

Supports multiple LLM providers:
1. Google Gemini (requires API key)
2. Ollama (FREE - runs locally)
3. OpenAI GPT (requires API key)

Set LLM_PROVIDER in .env to choose:
- "gemini" for Google Gemini
- "ollama" for free local LLM
- "openai" for OpenAI GPT
"""

import os
from dotenv import load_dotenv

load_dotenv()


# Cache for LLM instances
_llm_cache = {}

def get_llm():
    """
    Get LLM based on configured provider.
    Uses caching (Singleton pattern) to avoid re-initialization overhead.
    
    Environment variables:
        LLM_PROVIDER: gemini, ollama, or openai
        MODEL_NAME: specific model to use
        GOOGLE_API_KEY: for Gemini
        OPENAI_API_KEY: for OpenAI
    """
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    model_name = os.getenv("MODEL_NAME", "")
    temperature = float(os.getenv("TEMPERATURE", "0"))
    
    # Create cache key based on config
    cache_key = f"{provider}:{model_name}:{temperature}"
    
    if cache_key in _llm_cache:
        return _llm_cache[cache_key]
    
    llm = None
    if provider == "ollama":
        # FREE local LLM - no API key required
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            model=model_name or "llama3.2",
            temperature=temperature
        )
    
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model=model_name or "gpt-4o-mini",
            temperature=temperature,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    else:  # Default: gemini
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=model_name or "gemini-1.5-flash",
            temperature=temperature,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            convert_system_message_to_human=True,
            max_retries=3
        )
        
    _llm_cache[cache_key] = llm
    return llm


def get_provider_info() -> dict:
    """Get current LLM provider configuration."""
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    model_name = os.getenv("MODEL_NAME", "")
    
    info = {
        "provider": provider,
        "model": model_name,
        "requires_api_key": provider != "ollama"
    }
    
    if provider == "gemini":
        info["configured"] = bool(os.getenv("GOOGLE_API_KEY"))
        info["model"] = model_name or "gemini-1.5-flash"
    elif provider == "openai":
        info["configured"] = bool(os.getenv("OPENAI_API_KEY"))
        info["model"] = model_name or "gpt-4o-mini"
    else:
        info["configured"] = True  # Ollama doesn't need API key
        info["model"] = model_name or "llama3.2"
    
    return info


if __name__ == "__main__":
    print("LLM Provider Info:")
    print(get_provider_info())
