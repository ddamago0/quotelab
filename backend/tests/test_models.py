from app.domain.models import (
    Quote,
    QuoteMatch,
    SearchResult,
    DebateEssay,
    BatchItem,
    Batch,
    BatchReceipt,
)


def test_quote_model_instantiation():
    quote = Quote(
        id="q_001",
        text="Imagination is more important than knowledge.",
        author="Albert Einstein",
        tags=["imagination", "knowledge"],
    )
    assert quote.id == "q_001"
    assert quote.author == "Albert Einstein"
    assert len(quote.tags) == 2


def test_search_result_model_instantiation():
    quote = Quote(id="q_001", text="Test quote", author="Author", tags=[])
    match = QuoteMatch(quote=quote, similarity_score=0.88)
    search_res = SearchResult(query="Test query", matches=[match], total_found=1)
    assert search_res.query == "Test query"
    assert search_res.matches[0].similarity_score == 0.88


def test_debate_essay_model_instantiation():
    essay = DebateEssay(
        question="Is knowledge power?",
        sufficient_evidence=True,
        paragraphs=["Paragraph 1", "Paragraph 2"],
        evidence_quotes=[],
    )
    assert essay.sufficient_evidence is True
    assert len(essay.paragraphs) == 2

    refusal = DebateEssay(
        question="Unknown question?",
        sufficient_evidence=False,
        message="The database does not contain enough relevant evidence.",
    )
    assert refusal.sufficient_evidence is False
    assert refusal.message is not None


def test_batch_receipt_model_instantiation():
    item = BatchItem(quote_id="q_001", unit_count=25)
    batch = Batch(batch_id=1, items=[item], total_units=25)
    receipt = BatchReceipt(
        total_items_processed=1,
        total_units_consumed=25,
        total_batches_created=1,
        max_units_per_request=100,
        batches=[batch],
        failed_items=[],
    )
    assert receipt.total_items_processed == 1
    assert receipt.batches[0].total_units == 25
