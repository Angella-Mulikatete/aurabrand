import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

load_dotenv(override=True)

def get_model(provider: str = None, model_name: str = None):
    """
    Model factory to return a LangChain ChatModel based on provider.
    Defaults are loaded from .env if not specified.
    Falls back to Groq automatically if the primary provider fails.
    """
    provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "google").lower()

    if provider == "google":
        model = model_name or os.getenv("DEFAULT_LLM_MODEL", "gemini-2.0-flash")
        return ChatGoogleGenerativeAI(model=model)

    elif provider == "anthropic":
        model = model_name or os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
        return ChatAnthropic(model_name=model)

    elif provider == "openai":
        model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o")
        return ChatOpenAI(model=model)

    elif provider == "groq":
        model = model_name or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        return ChatGroq(model=model)

    elif provider == "openrouter":
        return ChatOpenAI(
            model=model_name or "meta-llama/llama-3-70b-instruct",
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=os.getenv("OPENROUTER_API_KEY")
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}")


def get_model_with_fallback(provider: str = None, model_name: str = None):
    """
    Tries the primary provider; automatically falls back to Groq on quota/rate errors.
    Uses LangChain's native .with_fallbacks() to handle errors during invocation.
    """
    primary_provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "google").lower()
    primary_model = get_model(primary_provider, model_name)
    
    # If the primary provider is already Groq, no fallback is needed
    if primary_provider == "groq":
        return primary_model

    # Create a fallback model (Groq is a reliable free-tier fallback)
    fallback_model = get_model("groq")
    
    # Return a model that automatically falls back to Groq if the primary fails
    return primary_model.with_fallbacks([fallback_model])


if __name__ == "__main__":
    try:
        m = get_model_with_fallback()
        print(f"Loaded model: {m.__class__.__name__}")
    except Exception as e:
        print(f"Error: {e}")
