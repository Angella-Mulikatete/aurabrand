import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

load_dotenv()

def get_model(provider: str = None, model_name: str = None):
    """
    Model factory to return a LangChain ChatModel based on provider.
    Defaults are loaded from .env if not specified.
    """
    provider = provider or os.getenv("DEFAULT_LLM_PROVIDER", "google").lower()
    
    if provider == "google":
        model = model_name or os.getenv("DEFAULT_LLM_MODEL", "gemini-1.5-pro")
        return ChatGoogleGenerativeAI(model=model)
    
    elif provider == "anthropic":
        model = model_name or os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")
        return ChatAnthropic(model_name=model)
    
    elif provider == "openai":
        model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o")
        return ChatOpenAI(model=model)
    
    elif provider == "groq":
        model = model_name or os.getenv("GROQ_MODEL", "llama3-70b-8192")
        return ChatGroq(model_name=model)
    
    # Fallback/OpenRouter could be implemented here as well
    elif provider == "openrouter":
        return ChatOpenAI(
            model=model_name or "meta-llama/llama-3-70b-instruct",
            openai_api_base="https://openrouter.ai/api/v1",
            openai_api_key=os.getenv("OPENROUTER_API_KEY")
        )
    
    else:
        raise ValueError(f"Unsupported provider: {provider}")

if __name__ == "__main__":
    # Test factory
    try:
        m = get_model("google")
        print(f"Loaded model: {m.__class__.__name__}")
    except Exception as e:
        print(f"Error: {e}")
