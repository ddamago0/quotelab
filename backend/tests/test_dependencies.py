import pytest
from app.config import settings
from app.api.dependencies import get_llm_provider
from app.infra.llm.mock_llm_provider import MockLLMProvider
from app.infra.llm.ollama_llm_provider import OllamaLLMProvider


def test_get_llm_provider_returns_mock_by_default(monkeypatch):
    """Verify that get_llm_provider returns MockLLMProvider when LLM_PROVIDER is mock-dev."""
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock-dev")
    get_llm_provider.cache_clear()

    provider = get_llm_provider()
    assert isinstance(provider, MockLLMProvider)


def test_get_llm_provider_returns_mock_for_alias(monkeypatch):
    """Verify that get_llm_provider returns MockLLMProvider when LLM_PROVIDER is 'mock'."""
    monkeypatch.setattr(settings, "LLM_PROVIDER", "mock")
    get_llm_provider.cache_clear()

    provider = get_llm_provider()
    assert isinstance(provider, MockLLMProvider)


def test_get_llm_provider_returns_ollama(monkeypatch):
    """Verify that get_llm_provider returns OllamaLLMProvider when LLM_PROVIDER is 'ollama'."""
    monkeypatch.setattr(settings, "LLM_PROVIDER", "ollama")
    monkeypatch.setattr(settings, "OLLAMA_BASE_URL", "http://localhost:11434")
    monkeypatch.setattr(settings, "OLLAMA_MODEL", "qwen2.5:3b")
    get_llm_provider.cache_clear()

    provider = get_llm_provider()
    assert isinstance(provider, OllamaLLMProvider)
    assert provider.base_url == "http://localhost:11434"
    assert provider.model == "qwen2.5:3b"


def test_get_llm_provider_unsupported_raises_value_error(monkeypatch):
    """Verify that unsupported LLM_PROVIDER setting raises ValueError."""
    monkeypatch.setattr(settings, "LLM_PROVIDER", "unsupported_provider")
    get_llm_provider.cache_clear()

    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER setting: 'unsupported_provider'"):
        get_llm_provider()
