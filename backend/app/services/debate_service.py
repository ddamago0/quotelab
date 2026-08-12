from typing import List, Optional
from app.domain.models import Quote, QuoteMatch, DebateResponse, DebateArgument
from app.domain.ports import LLMProviderPort
from app.services.semantic_retriever import SemanticRetriever
from app.config import settings


class DebateService:
    """
    Service responsible for evidence-backed debate generation.
    Follows clean architecture: depends only on SemanticRetriever abstraction and LLMProviderPort.
    Strictly prevents fabrication of quotes or citations.
    """

    def __init__(
        self,
        retriever: SemanticRetriever,
        llm_provider: LLMProviderPort,
        relevance_threshold: Optional[float] = None,
        max_evidence_quotes: Optional[int] = None,
    ):
        self.retriever = retriever
        self.llm_provider = llm_provider
        self.relevance_threshold = (
            relevance_threshold
            if relevance_threshold is not None
            else settings.DEBATE_RELEVANCE_THRESHOLD
        )
        self.max_evidence_quotes = (
            max_evidence_quotes
            if max_evidence_quotes is not None
            else settings.DEBATE_EVIDENCE_TOP_K
        )

    def generate_debate(
        self,
        topic: str,
        override_min_score: Optional[float] = None
    ) -> DebateResponse:
        """
        Generates a structured DebateResponse grounded strictly in retrieved evidence quotes.
        If no retrieved evidence meets the relevance threshold, returns a controlled refusal response.
        """
        if not topic or not topic.strip():
            raise ValueError("Debate topic cannot be empty or whitespace.")

        cleaned_topic = topic.strip()
        threshold = override_min_score if override_min_score is not None else self.relevance_threshold

        # Step 1: Retrieve candidate evidence using SemanticRetriever
        candidate_matches: List[QuoteMatch] = self.retriever.search(
            query=cleaned_topic,
            top_k=self.max_evidence_quotes
        )

        # Step 2: Filter candidate matches against relevance threshold
        qualified_matches = [
            match for match in candidate_matches if match.similarity_score >= threshold
        ]

        # Step 3: Handle insufficient evidence safely (NEVER fabricate quotes)
        if not qualified_matches:
            return DebateResponse(
                topic=cleaned_topic,
                sufficient_evidence=False,
                arguments=[],
                evidence_quotes=[],
                refusal_message=(
                    "Insufficient relevant evidence found in the quote corpus to construct "
                    f"a grounded debate for topic: '{cleaned_topic}'."
                )
            )

        # Step 4: Extract qualified verbatim quotes
        qualified_quotes: List[Quote] = [m.quote for m in qualified_matches]

        # Step 5: Delegate argument generation to the LLMProviderPort
        arguments: List[DebateArgument] = self.llm_provider.generate_debate_arguments(
            topic=cleaned_topic,
            evidence_quotes=qualified_quotes
        )

        # Step 6: Return structured response with evidence grounding and attribution
        return DebateResponse(
            topic=cleaned_topic,
            sufficient_evidence=True,
            arguments=arguments,
            evidence_quotes=qualified_quotes,
            refusal_message=None
        )
