from typing import List, Optional
from app.domain.models import Quote, BatchItem, Batch, BatchReceipt
from app.domain.ports import QuoteRepositoryPort, TokenizerPort
from app.config import settings


class BatchOptimizerService:
    """
    Service responsible for packing quote items into batches respecting unit capacity limits.
    Uses a deterministic greedy algorithm to maximize quote throughput.
    Follows Clean Architecture: depends only on QuoteRepositoryPort and TokenizerPort abstractions.
    """

    def __init__(
        self,
        quote_repository: QuoteRepositoryPort,
        tokenizer: TokenizerPort,
        max_units_per_batch: Optional[int] = None,
    ):
        self.quote_repository = quote_repository
        self.tokenizer = tokenizer
        self.max_units_per_batch = (
            max_units_per_batch
            if max_units_per_batch is not None
            else settings.MAX_UNITS_PER_BATCH
        )

    def optimize_batches(
        self,
        quote_ids: Optional[List[str]] = None,
        override_max_units: Optional[int] = None
    ) -> BatchReceipt:
        """
        Packs requested quotes (or all quotes if quote_ids is None/empty) into batches.
        Enforces maximum unit capacity per batch.
        Items exceeding capacity on their own are identified as failed_items and not dropped silently.
        """
        capacity = override_max_units if override_max_units is not None else self.max_units_per_batch
        if capacity <= 0:
            raise ValueError("Max units per batch capacity must be a positive integer > 0.")

        # Step 1: Resolve target quotes
        target_quotes: List[Quote] = []
        if quote_ids is None:
            target_quotes = self.quote_repository.get_all_quotes()
        else:
            for qid in quote_ids:
                quote = self.quote_repository.get_quote_by_id(qid)
                if not quote:
                    raise ValueError(f"Quote with ID '{qid}' not found in repository.")
                target_quotes.append(quote)

        if not target_quotes:
            return BatchReceipt(
                total_items_processed=0,
                total_units_consumed=0,
                total_batches_created=0,
                max_units_per_request=capacity,
                batches=[],
                failed_items=[]
            )

        # Step 2: Calculate units and segregate items exceeding capacity
        eligible_items: List[BatchItem] = []
        failed_items: List[str] = []

        for quote in target_quotes:
            units = self.tokenizer.count_units(quote.text)
            if units > capacity:
                failed_items.append(quote.id)
            else:
                eligible_items.append(BatchItem(quote_id=quote.id, unit_count=units))

        # Step 3: Greedy batch packing
        batches: List[Batch] = []
        current_items: List[BatchItem] = []
        current_units: int = 0

        for item in eligible_items:
            if not current_items:
                current_items.append(item)
                current_units = item.unit_count
            elif current_units + item.unit_count <= capacity:
                current_items.append(item)
                current_units += item.unit_count
            else:
                # Close current batch and open a new one
                batch_id = len(batches) + 1
                batches.append(Batch(batch_id=batch_id, items=current_items, total_units=current_units))
                current_items = [item]
                current_units = item.unit_count

        # Close final batch if non-empty
        if current_items:
            batch_id = len(batches) + 1
            batches.append(Batch(batch_id=batch_id, items=current_items, total_units=current_units))

        total_units_consumed = sum(b.total_units for b in batches)

        return BatchReceipt(
            total_items_processed=len(target_quotes),
            total_units_consumed=total_units_consumed,
            total_batches_created=len(batches),
            max_units_per_request=capacity,
            batches=batches,
            failed_items=failed_items
        )
