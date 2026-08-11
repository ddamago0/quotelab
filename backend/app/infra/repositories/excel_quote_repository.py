from pathlib import Path
from typing import List, Dict, Optional
import openpyxl

from app.domain.models import Quote
from app.domain.ports import QuoteRepositoryPort


class DatasetValidationError(ValueError):
    """Raised when the Excel dataset fails contract or integrity validation."""
    pass


class ExcelQuoteRepository(QuoteRepositoryPort):
    """
    Concrete repository implementation that loads and validates quotes from an Excel dataset (.xlsx).
    Implements QuoteRepositoryPort.
    """

    EXPECTED_QUOTE_COUNT = 100

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        self._quotes: List[Quote] = []
        self._quotes_by_id: Dict[str, Quote] = {}
        self._load_and_validate()

    def _load_and_validate(self) -> None:
        if not self.file_path.exists():
            raise DatasetValidationError(f"Dataset file not found at: {self.file_path.resolve()}")

        try:
            workbook = openpyxl.load_workbook(str(self.file_path), data_only=True)
        except Exception as e:
            raise DatasetValidationError(f"Failed to open Excel dataset file: {str(e)}") from e

        sheet = workbook.active
        if sheet is None:
            raise DatasetValidationError("Excel workbook contains no active worksheet")

        rows = list(sheet.iter_rows(values_only=True))
        if not rows or len(rows) < 2:
            raise DatasetValidationError("Excel sheet is empty or lacks header and data rows")

        # Header validation
        header = [str(cell).strip().lower() if cell is not None else "" for cell in rows[0]]
        
        if "author" not in header:
            raise DatasetValidationError("Dataset missing required column: 'author'")
        if "phrase" not in header:
            raise DatasetValidationError("Dataset missing required column: 'phrase'")

        author_col_idx = header.index("author")
        phrase_col_idx = header.index("phrase")

        seen_phrases = set()
        loaded_quotes: List[Quote] = []

        # Row validation and parsing (starting from row index 2 in Excel)
        for excel_row_num, row in enumerate(rows[1:], start=2):
            # Skip completely empty rows at the end if any
            if not row or all(cell is None or str(cell).strip() == "" for cell in row):
                continue

            author_val = row[author_col_idx] if author_col_idx < len(row) else None
            phrase_val = row[phrase_col_idx] if phrase_col_idx < len(row) else None

            author = str(author_val).strip() if author_val is not None else ""
            phrase = str(phrase_val).strip() if phrase_val is not None else ""

            if not author:
                raise DatasetValidationError(f"Row {excel_row_num}: author must be non-empty")
            if not phrase:
                raise DatasetValidationError(f"Row {excel_row_num}: phrase must be non-empty")

            phrase_normalized = phrase.lower()
            if phrase_normalized in seen_phrases:
                raise DatasetValidationError(f"Row {excel_row_num}: duplicate phrase detected: '{phrase[:40]}...'")

            seen_phrases.add(phrase_normalized)
            quote_id = f"q_{len(loaded_quotes) + 1}"
            
            quote = Quote(
                id=quote_id,
                text=phrase,
                author=author,
                tags=[]
            )
            loaded_quotes.append(quote)

        # Total count validation
        if len(loaded_quotes) != self.EXPECTED_QUOTE_COUNT:
            raise DatasetValidationError(
                f"Expected exactly {self.EXPECTED_QUOTE_COUNT} valid quotes, but loaded {len(loaded_quotes)}"
            )

        self._quotes = loaded_quotes
        self._quotes_by_id = {q.id: q for q in loaded_quotes}

    def get_all_quotes(self) -> List[Quote]:
        """Retrieves all 100 domain quotes."""
        return list(self._quotes)

    def get_quote_by_id(self, quote_id: str) -> Optional[Quote]:
        """Retrieves a quote by unique ID (e.g. 'q_1')."""
        return self._quotes_by_id.get(quote_id)
