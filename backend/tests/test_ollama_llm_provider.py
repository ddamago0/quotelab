import json
import pytest
import httpx
from typing import List

from app.domain.models import Quote, DebateArgument
from app.infra.llm.ollama_llm_provider import OllamaLLMProvider, OllamaProviderError


@pytest.fixture
def sample_quotes() -> List[Quote]:
    return [
        Quote(id="q1", text="La libertad de expresión es fundamental.", author="Autor 1", tags=["libertad"]),
        Quote(id="q2", text="La privacidad protege al individuo.", author="Autor 2", tags=["privacidad"]),
    ]


def test_generate_success():
    """Verify successful text generation via Ollama LLM provider."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        payload = json.loads(request.read())
        assert payload["model"] == "qwen2.5:3b"
        assert payload["stream"] is False
        assert payload["messages"][0]["content"] == "You are a helpful assistant"
        assert payload["messages"][1]["content"] == "Hello LLM"

        return httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you?"
                }
            }
        )

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(base_url="http://localhost:11434", model="qwen2.5:3b", client=client)

    result = provider.generate("Hello LLM", system_prompt="You are a helpful assistant")
    assert result == "Hello! How can I help you?"


def test_generate_empty_prompt_raises_value_error():
    """Verify empty prompt raises ValueError."""
    provider = OllamaLLMProvider()
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        provider.generate("   ")


def test_generate_debate_arguments_success(sample_quotes):
    """Verify successful structured debate argument generation."""
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/chat"
        payload = json.loads(request.read())
        assert payload["format"] == "json"

        mock_response_body = {
            "arguments": [
                {
                    "position": "A favor",
                    "argument_text": "La libertad debe ser protegida siempre.",
                    "evidence_quote_ids": ["q1"]
                },
                {
                    "position": "En contra",
                    "argument_text": "La privacidad debe balancearse con la seguridad.",
                    "evidence_quote_ids": ["q2"]
                }
            ]
        }
        return httpx.Response(
            200,
            json={"message": {"content": json.dumps(mock_response_body)}}
        )

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(client=client)

    args = provider.generate_debate_arguments(
        topic="Libertad vs Privacidad",
        evidence_quotes=sample_quotes
    )

    assert len(args) == 2
    assert isinstance(args[0], DebateArgument)
    assert args[0].position == "A favor"
    assert args[0].evidence_quote_ids == ["q1"]
    assert args[1].position == "En contra"
    assert args[1].evidence_quote_ids == ["q2"]


def test_generate_debate_arguments_empty_evidence():
    """Verify empty evidence quotes list returns empty arguments list without HTTP call."""
    provider = OllamaLLMProvider()
    res = provider.generate_debate_arguments("Tema", [])
    assert res == []


def test_generate_debate_arguments_markdown_fenced_json(sample_quotes):
    """Verify parsing of JSON wrapped in markdown code fences."""
    def handler(request: httpx.Request) -> httpx.Response:
        content = """```json
[
  {
    "position": "Perspectiva A",
    "argument_text": "Texto descriptivo.",
    "evidence_quote_ids": ["q1"]
  }
]
```"""
        return httpx.Response(200, json={"message": {"content": content}})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(client=client)

    args = provider.generate_debate_arguments("Tema", sample_quotes)
    assert len(args) == 1
    assert args[0].position == "Perspectiva A"
    assert args[0].evidence_quote_ids == ["q1"]


def test_grounding_filters_invented_quote_ids(sample_quotes):
    """Verify that quote IDs not present in evidence_quotes are filtered out."""
    def handler(request: httpx.Request) -> httpx.Response:
        content = json.dumps({
            "arguments": [
                {
                    "position": "A favor",
                    "argument_text": "Argumento.",
                    "evidence_quote_ids": ["q1", "fake_id_999"]
                }
            ]
        })
        return httpx.Response(200, json={"message": {"content": content}})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(client=client)

    args = provider.generate_debate_arguments("Tema", sample_quotes)
    assert len(args) == 1
    assert args[0].evidence_quote_ids == ["q1"]
    assert "fake_id_999" not in args[0].evidence_quote_ids


def test_http_error_handling():
    """Verify HTTP status error (500) raises OllamaProviderError."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="Internal Server Error")

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(client=client)

    with pytest.raises(OllamaProviderError, match="HTTP status 500"):
        provider.generate("Test prompt")


def test_connection_error_handling():
    """Verify connection error raises OllamaProviderError."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(client=client)

    with pytest.raises(OllamaProviderError, match="Failed to connect"):
        provider.generate("Test prompt")


def test_timeout_error_handling():
    """Verify timeout error raises OllamaProviderError."""
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("Read timed out")

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(client=client)

    with pytest.raises(OllamaProviderError, match="timed out"):
        provider.generate("Test prompt")


def test_invalid_json_handling(sample_quotes):
    """Verify malformed JSON content raises OllamaProviderError."""
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"message": {"content": "{invalid json syntax..."}})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(client=client)

    with pytest.raises(OllamaProviderError, match="Failed to parse Ollama model response as JSON"):
        provider.generate_debate_arguments("Tema", sample_quotes)


def test_invalid_debate_argument_structure_handling(sample_quotes):
    """Verify response missing required fields raises OllamaProviderError."""
    def handler(request: httpx.Request) -> httpx.Response:
        bad_structure = [{"position": "A favor", "evidence_quote_ids": ["q1"]}]
        return httpx.Response(200, json={"message": {"content": json.dumps(bad_structure)}})

    transport = httpx.MockTransport(handler)
    client = httpx.Client(transport=transport)
    provider = OllamaLLMProvider(client=client)

    with pytest.raises(OllamaProviderError, match="missing valid 'argument_text'"):
        provider.generate_debate_arguments("Tema", sample_quotes)
