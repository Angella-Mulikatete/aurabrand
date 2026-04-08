import pytest
import os
from unittest.mock import patch, MagicMock
from src.factory import get_model, get_model_with_fallback
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq

def test_get_model_google():
    with patch.dict(os.environ, {"DEFAULT_LLM_PROVIDER": "google", "DEFAULT_LLM_MODEL": "gemini-2.0-flash"}):
        model = get_model()
        assert isinstance(model, ChatGoogleGenerativeAI)
        assert model.model == "gemini-2.0-flash"

def test_get_model_groq():
    with patch.dict(os.environ, {"DEFAULT_LLM_PROVIDER": "groq", "GROQ_MODEL": "llama-3.3-70b-versatile"}):
        model = get_model()
        assert isinstance(model, ChatGroq)
        assert model.model_name == "llama-3.3-70b-versatile"

def test_get_model_with_fallback_logic():
    """
    Test that get_model_with_fallback returns a model with fallbacks configured.
    """
    with patch.dict(os.environ, {"DEFAULT_LLM_PROVIDER": "google"}):
        model = get_model_with_fallback()
        # LangChain's .with_fallbacks() returns a RunnableWithFallbacks
        assert hasattr(model, "fallbacks")
        assert len(model.fallbacks) > 0
        assert isinstance(model.fallbacks[0], ChatGroq)
