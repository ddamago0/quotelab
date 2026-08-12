from typing import List, Optional
from app.domain.models import Quote, DebateArgument
from app.domain.ports import LLMProviderPort


class MockLLMProvider(LLMProviderPort):
    """
    Deterministic mock provider implementing LLMProviderPort.
    Used for local development and testing without requiring API keys, cloud access, or an active local LLM.
    
    WARNING: This is a synthetic development provider. It produces reproducible, structured debate arguments
    grounded strictly in the provided evidence quotes without performing actual neural text synthesis.
    """

    def __init__(self, provider_name: str = "mock-dev-llm"):
        self.provider_name = provider_name

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Produces a deterministic mock text completion."""
        sys_prefix = f"[{system_prompt}] " if system_prompt else ""
        return f"{sys_prefix}[MOCK_LLM_OUTPUT ({self.provider_name})]: Response for prompt: '{prompt[:50]}...'"

    def generate_debate_arguments(
        self,
        topic: str,
        evidence_quotes: List[Quote]
    ) -> List[DebateArgument]:
        """
        Generates deterministic debate arguments from evidence quotes.
        Strictly preserves quote attribution by citing the exact evidence quote IDs.
        """
        if not evidence_quotes:
            return []

        arguments: List[DebateArgument] = []

        # Produce balanced perspectives using the retrieved quotes as grounding
        for idx, quote in enumerate(evidence_quotes, start=1):
            stance = "Perspectiva A (A favor)" if idx % 2 != 0 else "Perspectiva B (En contra)"
            argument_text = (
                f"[DESARROLLO MOCK] En relación con el debate '{topic}', "
                f"{quote.author} ofrece evidencia clave: \"{quote.text}\"."
            )
            arguments.append(
                DebateArgument(
                    position=stance,
                    argument_text=argument_text,
                    evidence_quote_ids=[quote.id]
                )
            )

        return arguments
