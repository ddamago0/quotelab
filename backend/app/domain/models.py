from pydantic import BaseModel, Field
from typing import List, Optional


class Quote(BaseModel):
    """Core domain model representing a single quote entity."""
    id: str = Field(..., description="Unique identifier for the quote")
    text: str = Field(..., description="The quote verbatim content")
    author: str = Field(..., description="Author or attribution of the quote")
    tags: List[str] = Field(default_factory=list, description="Associated tags or categories")


class QuoteMatch(BaseModel):
    """Model representing a quote retrieved with a semantic similarity score."""
    quote: Quote
    similarity_score: float = Field(..., ge=-1.0, le=1.0, description="Cosine similarity score")


class SearchResult(BaseModel):
    """Response payload for Semantic Vibe Search challenge."""
    query: str
    matches: List[QuoteMatch]
    total_found: int


class DebateEssay(BaseModel):
    """Response payload for Evidence-Backed Debate challenge."""
    question: str
    sufficient_evidence: bool = Field(..., description="True if retrieved sources satisfy relevance threshold")
    paragraphs: List[str] = Field(default_factory=list, description="Array of essay paragraphs (exactly 2 when sufficient evidence)")
    evidence_quotes: List[Quote] = Field(default_factory=list, description="Verbatim quotes used as evidence")
    message: Optional[str] = Field(default=None, description="Explicit refusal message if evidence is insufficient")


class BatchItem(BaseModel):
    """Individual item unit measurement within a batch."""
    quote_id: str
    unit_count: int = Field(..., ge=0)


class Batch(BaseModel):
    """Group of quotes packed within unit capacity limit."""
    batch_id: int
    items: List[BatchItem]
    total_units: int


class BatchReceipt(BaseModel):
    """Response payload for Budget & Batching Optimizer challenge."""
    total_items_processed: int
    total_units_consumed: int
    total_batches_created: int
    max_units_per_request: int
    batches: List[Batch]
    failed_items: List[str] = Field(default_factory=list, description="IDs of items exceeding capacity on their own")
