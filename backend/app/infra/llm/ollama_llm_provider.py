import json
from typing import List, Optional, Dict, Any, Set
import httpx

from app.config import settings
from app.domain.models import Quote, DebateArgument
from app.domain.ports import LLMProviderPort


class OllamaProviderError(Exception):
    """Controlled application-level exception for Ollama provider errors."""
    pass


class OllamaLLMProvider(LLMProviderPort):
    """
    Adapter implementing LLMProviderPort to interface with a locally running Ollama LLM.
    Communicates via Ollama's HTTP REST API (/api/chat) using httpx.
    Strictly local, provider-agnostic, and decoupled from cloud APIs or vendor SDKs.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[float] = None,
        client: Optional[httpx.Client] = None,
    ):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout if timeout is not None else settings.OLLAMA_TIMEOUT
        self._client = client

    def _post_chat(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sends a POST request to Ollama's /api/chat endpoint.
        Handles network errors, HTTP errors, and timeouts gracefully.
        """
        url = f"{self.base_url}/api/chat"
        try:
            if self._client is not None:
                response = self._client.post(url, json=payload, timeout=self.timeout)
            else:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise OllamaProviderError(f"Ollama API returned non-dict response payload: {type(data)}")
            return data
        except httpx.TimeoutException as exc:
            raise OllamaProviderError(f"Ollama request timed out after {self.timeout}s: {exc}") from exc
        except httpx.ConnectError as exc:
            raise OllamaProviderError(f"Failed to connect to Ollama service at {self.base_url}: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise OllamaProviderError(
                f"Ollama API returned HTTP status {exc.response.status_code}: {exc.response.text}"
            ) from exc
        except httpx.RequestError as exc:
            raise OllamaProviderError(f"Ollama HTTP request error: {exc}") from exc
        except OllamaProviderError:
            raise
        except Exception as exc:
            raise OllamaProviderError(f"Unexpected error communicating with Ollama: {exc}") from exc

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generates text completion based on prompt and optional system instructions.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty or whitespace.")

        messages = []
        if system_prompt and system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt.strip()})
        messages.append({"role": "user", "content": prompt.strip()})

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
        }

        data = self._post_chat(payload)
        
        message = data.get("message")
        if not isinstance(message, dict) or "content" not in message:
            raise OllamaProviderError(f"Ollama response payload missing 'message.content': {data}")

        content = message["content"]
        if not isinstance(content, str):
            raise OllamaProviderError(f"Ollama response 'message.content' must be a string, got {type(content)}")

        return content

    def _clean_and_parse_json(self, raw_content: str) -> Any:
        """
        Defensively cleans and parses JSON content returned by local LLMs.
        Strips markdown code fences (e.g. ```json ... ```) if present.
        """
        if not raw_content or not raw_content.strip():
            raise OllamaProviderError("Received empty response content from Ollama model.")

        cleaned = raw_content.strip()

        # Handle markdown fence wrapping if present
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            # Remove opening fence line (e.g., ```json or ```)
            if lines[0].startswith("```"):
                lines = lines[1:]
            # Remove trailing fence line if present
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise OllamaProviderError(
                f"Failed to parse Ollama model response as JSON: {exc}. Content snippet: {raw_content[:200]!r}"
            ) from exc

    def generate_debate_arguments(
        self,
        topic: str,
        evidence_quotes: List[Quote]
    ) -> List[DebateArgument]:
        """
        Generates structured debate arguments grounded strictly in the provided evidence quotes.
        Prevents fabrication of evidence or quote IDs.
        """
        if not topic or not topic.strip():
            raise ValueError("Debate topic cannot be empty or whitespace.")

        if not evidence_quotes:
            return []

        valid_quote_ids: Set[str] = {q.id for q in evidence_quotes}

        formatted_quotes = []
        for q in evidence_quotes:
            formatted_quotes.append(f"- ID: {q.id}\n  Autor: {q.author}\n  Texto: \"{q.text}\"")
        quotes_block = "\n".join(formatted_quotes)

        system_prompt = (
            "Eres un analista de debate riguroso y objetivo.\n"
            "REGLAS ESTRUCTURALES Y DE ATRIBUCIÓN:\n"
            "1. Debes generar argumentos de debate estructurados basados ÚNICAMENTE en las citas provistas.\n"
            "2. NUNCA inventes IDs de citas, frases o autores.\n"
            "3. Cada 'evidence_quote_ids' DEBE corresponder únicamente a los IDs presentes en la lista de evidencia provista.\n"
            "4. Si la evidencia es insuficiente, no inventes citas adicionales.\n"
            "5. Responde estrictamente con un objeto JSON con la siguiente estructura exacta:\n"
            "{\n"
            '  "arguments": [\n'
            '    {\n'
            '      "position": "Perspectiva o postura (ej. A favor / En contra)",\n'
            '      "argument_text": "Explicación del argumento basada estrictamente en la evidencia",\n'
            '      "evidence_quote_ids": ["ID_DE_CITA_USADO"]\n'
            '    }\n'
            '  ]\n'
            "}"
        )

        user_prompt = f"Tema de debate: {topic.strip()}\n\nCitas de evidencia disponibles:\n{quotes_block}"

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "stream": False,
            "format": "json"
        }

        data = self._post_chat(payload)
        message = data.get("message")
        if not isinstance(message, dict) or "content" not in message:
            raise OllamaProviderError(f"Ollama response payload missing 'message.content': {data}")

        raw_content = message["content"]
        if not isinstance(raw_content, str):
            raise OllamaProviderError(f"Ollama response 'message.content' must be a string, got {type(raw_content)}")

        parsed_json = self._clean_and_parse_json(raw_content)

        # Normalize JSON structure (list of dicts, or dict with 'arguments' / 'debate_arguments' key)
        if isinstance(parsed_json, list):
            items_list = parsed_json
        elif isinstance(parsed_json, dict):
            if "arguments" in parsed_json and isinstance(parsed_json["arguments"], list):
                items_list = parsed_json["arguments"]
            elif "debate_arguments" in parsed_json and isinstance(parsed_json["debate_arguments"], list):
                items_list = parsed_json["debate_arguments"]
            elif "position" in parsed_json and "argument_text" in parsed_json:
                items_list = [parsed_json]
            else:
                raise OllamaProviderError(
                    f"Parsed JSON dictionary does not contain an 'arguments' list or argument fields. Keys: {list(parsed_json.keys())}"
                )
        else:
            raise OllamaProviderError(f"Expected JSON list or object for debate arguments, got {type(parsed_json)}")

        debate_arguments: List[DebateArgument] = []
        for idx, item in enumerate(items_list):
            if not isinstance(item, dict):
                raise OllamaProviderError(f"Item at index {idx} in debate arguments is not a JSON object: {type(item)}")

            position = item.get("position")
            argument_text = item.get("argument_text")
            raw_quote_ids = item.get("evidence_quote_ids")

            if not position or not isinstance(position, str) or not position.strip():
                raise OllamaProviderError(f"Item at index {idx} missing valid 'position' string: {item}")

            if not argument_text or not isinstance(argument_text, str) or not argument_text.strip():
                raise OllamaProviderError(f"Item at index {idx} missing valid 'argument_text' string: {item}")

            if not isinstance(raw_quote_ids, list):
                raise OllamaProviderError(f"Item at index {idx} missing valid 'evidence_quote_ids' list: {item}")

            # Grounding check: filter out any ID not present in supplied evidence_quotes
            grounded_quote_ids = [str(qid) for qid in raw_quote_ids if str(qid) in valid_quote_ids]

            debate_arguments.append(
                DebateArgument(
                    position=position.strip(),
                    argument_text=argument_text.strip(),
                    evidence_quote_ids=grounded_quote_ids
                )
            )

        return debate_arguments
