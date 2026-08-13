import os
import pytest
import httpx
from app.config import settings
from app.infra.llm.ollama_llm_provider import OllamaLLMProvider, OllamaProviderError

RUN_REAL_OLLAMA = os.getenv("RUN_REAL_OLLAMA_TESTS") == "1"


def _is_ollama_running(base_url: str) -> bool:
    """Helper to check if Ollama HTTP daemon is active and responsive."""
    try:
        url = f"{base_url.rstrip('/')}/api/tags"
        response = httpx.get(url, timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


@pytest.mark.skipif(
    not RUN_REAL_OLLAMA,
    reason="Real Ollama integration tests are skipped unless RUN_REAL_OLLAMA_TESTS=1 environment variable is set."
)
def test_real_ollama_provider_generate():
    """
    Optional real integration test verifying communication with a locally running Ollama daemon.
    Skipped by default in standard test suites.
    """
    if not _is_ollama_running(settings.OLLAMA_BASE_URL):
        pytest.skip(f"Ollama daemon is not running or unreachable at {settings.OLLAMA_BASE_URL}.")

    provider = OllamaLLMProvider(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        timeout=settings.OLLAMA_TIMEOUT,
    )

    try:
        response = provider.generate(
            prompt="Responde únicamente con la palabra 'Hola'.",
            system_prompt="Eres un asistente conciso."
        )
        assert isinstance(response, str)
        assert len(response.strip()) > 0
    except OllamaProviderError as exc:
        pytest.fail(f"Real Ollama communication failed: {exc}")
