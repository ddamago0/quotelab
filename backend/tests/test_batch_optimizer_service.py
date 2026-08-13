import pytest
from typing import List, Optional
from app.domain.models import Quote
from app.domain.ports import QuoteRepositoryPort, TokenizerPort
from app.services.batch_optimizer_service import BatchOptimizerService
from app.infra.tokenizer.local_tokenizer import LocalTokenizer


class DummyQuoteRepository(QuoteRepositoryPort):
    def __init__(self, quotes: List[Quote]):
        self.quotes = quotes
        self._by_id = {q.id: q for q in quotes}

    def get_all_quotes(self) -> List[Quote]:
        return list(self.quotes)

    def get_quote_by_id(self, quote_id: str) -> Optional[Quote]:
        return self._by_id.get(quote_id)


def test_batch_optimizer_empty_repository():
    repo = DummyQuoteRepository([])
    tokenizer = LocalTokenizer()
    service = BatchOptimizerService(quote_repository=repo, tokenizer=tokenizer, max_units_per_batch=100)

    receipt = service.optimize_batches()
    assert receipt.total_items_processed == 0
    assert receipt.total_units_consumed == 0
    assert receipt.total_batches_created == 0
    assert receipt.batches == []
    assert receipt.failed_items == []


def test_batch_optimizer_single_quote():
    q1 = Quote(id="q_1", text="Cinco palabras de prueba aqui", author="Autor 1", tags=[])
    repo = DummyQuoteRepository([q1])
    tokenizer = LocalTokenizer()
    service = BatchOptimizerService(quote_repository=repo, tokenizer=tokenizer, max_units_per_batch=10)

    receipt = service.optimize_batches()
    assert receipt.total_items_processed == 1
    assert receipt.total_units_consumed == 5
    assert receipt.total_batches_created == 1
    assert len(receipt.batches[0].items) == 1
    assert receipt.batches[0].items[0].quote_id == "q_1"
    assert receipt.batches[0].items[0].unit_count == 5


def test_batch_optimizer_multiple_quotes_single_batch():
    q1 = Quote(id="q_1", text="Dos palabras", author="Autor 1", tags=[])
    q2 = Quote(id="q_2", text="Tres palabras mas", author="Autor 2", tags=[])
    repo = DummyQuoteRepository([q1, q2])
    tokenizer = LocalTokenizer()
    service = BatchOptimizerService(quote_repository=repo, tokenizer=tokenizer, max_units_per_batch=10)

    receipt = service.optimize_batches()
    assert receipt.total_items_processed == 2
    assert receipt.total_units_consumed == 5
    assert receipt.total_batches_created == 1
    assert len(receipt.batches[0].items) == 2


def test_batch_optimizer_multiple_batches_greedy():
    # 4 words each
    q1 = Quote(id="q_1", text="Uno dos tres cuatro", author="A1", tags=[])
    q2 = Quote(id="q_2", text="Cinco seis siete ocho", author="A2", tags=[])
    q3 = Quote(id="q_3", text="Nueve diez once doce", author="A3", tags=[])
    repo = DummyQuoteRepository([q1, q2, q3])
    tokenizer = LocalTokenizer()
    # Capacity = 6: q1 (4 units) fits in Batch 1. q2 (4 units) cannot fit in Batch 1 (4+4=8 > 6), so starts Batch 2. q3 starts Batch 3.
    service = BatchOptimizerService(quote_repository=repo, tokenizer=tokenizer, max_units_per_batch=6)

    receipt = service.optimize_batches()
    assert receipt.total_items_processed == 3
    assert receipt.total_batches_created == 3
    assert receipt.total_units_consumed == 12
    assert receipt.batches[0].items[0].quote_id == "q_1"
    assert receipt.batches[1].items[0].quote_id == "q_2"
    assert receipt.batches[2].items[0].quote_id == "q_3"


def test_batch_optimizer_exact_capacity_fit():
    q1 = Quote(id="q_1", text="Cinco palabras de prueba aqui", author="A1", tags=[]) # 5 units
    repo = DummyQuoteRepository([q1])
    tokenizer = LocalTokenizer()
    service = BatchOptimizerService(quote_repository=repo, tokenizer=tokenizer, max_units_per_batch=5)

    receipt = service.optimize_batches()
    assert receipt.total_batches_created == 1
    assert receipt.batches[0].total_units == 5
    assert receipt.failed_items == []


def test_batch_optimizer_item_exceeding_capacity_added_to_failed_items():
    q1 = Quote(id="q_1", text="Dos palabras", author="A1", tags=[]) # 2 units
    q2 = Quote(id="q_2", text="Esta frase tiene demasiadas palabras para la capacidad maxima de la prueba", author="A2", tags=[]) # 11 units
    repo = DummyQuoteRepository([q1, q2])
    tokenizer = LocalTokenizer()
    service = BatchOptimizerService(quote_repository=repo, tokenizer=tokenizer, max_units_per_batch=5)

    receipt = service.optimize_batches()
    assert receipt.total_items_processed == 2
    assert receipt.total_batches_created == 1
    assert receipt.batches[0].items[0].quote_id == "q_1"
    assert receipt.failed_items == ["q_2"]


def test_batch_optimizer_quote_ids_filter_and_non_existent():
    q1 = Quote(id="q_1", text="Texto 1", author="A1", tags=[])
    repo = DummyQuoteRepository([q1])
    tokenizer = LocalTokenizer()
    service = BatchOptimizerService(quote_repository=repo, tokenizer=tokenizer, max_units_per_batch=100)

    receipt = service.optimize_batches(quote_ids=["q_1"])
    assert receipt.total_items_processed == 1

    with pytest.raises(ValueError, match="Quote with ID 'non_existent' not found"):
        service.optimize_batches(quote_ids=["non_existent"])


def test_batch_optimizer_invalid_capacity_raises_value_error():
    repo = DummyQuoteRepository([])
    tokenizer = LocalTokenizer()
    service = BatchOptimizerService(quote_repository=repo, tokenizer=tokenizer, max_units_per_batch=100)

    with pytest.raises(ValueError, match="Max units per batch capacity must be a positive integer > 0."):
        service.optimize_batches(override_max_units=0)
