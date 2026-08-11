import pytest
from pathlib import Path
import openpyxl

from app.infra.repositories.excel_quote_repository import (
    ExcelQuoteRepository,
    DatasetValidationError,
)
from app.domain.ports import QuoteRepositoryPort


def test_real_dataset_loads_successfully():
    """Verify loading the real data/citas.xlsx file produces exactly 100 valid Quote domain objects."""
    # Find dataset path relative to repository root
    project_root = Path(__file__).resolve().parent.parent.parent
    dataset_path = project_root / "data" / "citas.xlsx"

    assert dataset_path.exists(), f"Real dataset missing at {dataset_path}"

    repo = ExcelQuoteRepository(dataset_path)

    # Satisfies QuoteRepositoryPort interface
    assert isinstance(repo, QuoteRepositoryPort)

    all_quotes = repo.get_all_quotes()
    assert len(all_quotes) == 100

    # Check first and last quotes
    first_quote = all_quotes[0]
    assert first_quote.id == "q_1"
    assert bool(first_quote.author)
    assert bool(first_quote.text)

    # Check get_quote_by_id
    retrieved = repo.get_quote_by_id("q_50")
    assert retrieved is not None
    assert retrieved.id == "q_50"


def create_temp_excel(tmp_path: Path, filename: str, rows: list) -> Path:
    """Helper to create temporary .xlsx files for validation testing."""
    file_path = tmp_path / filename
    wb = openpyxl.Workbook()
    ws = wb.active
    for row in rows:
        ws.append(row)
    wb.save(file_path)
    return file_path


def test_missing_file_raises_validation_error(tmp_path: Path):
    non_existent = tmp_path / "does_not_exist.xlsx"
    with pytest.raises(DatasetValidationError, match="file not found"):
        ExcelQuoteRepository(non_existent)


def test_missing_required_columns_raises_validation_error(tmp_path: Path):
    # Missing 'author' column
    file_path = create_temp_excel(
        tmp_path,
        "bad_headers.xlsx",
        [["wrong_header", "phrase"], ["Some Author", "Some phrase"]],
    )
    with pytest.raises(DatasetValidationError, match="missing required column: 'author'"):
        ExcelQuoteRepository(file_path)


def test_empty_author_raises_validation_error(tmp_path: Path):
    rows = [["author", "phrase"]]
    for i in range(99):
        rows.append([f"Author {i}", f"Phrase number {i}"])
    rows.append(["   ", "Valid phrase for row 100"])  # Empty author

    file_path = create_temp_excel(tmp_path, "empty_author.xlsx", rows)
    with pytest.raises(DatasetValidationError, match="Row 101: author must be non-empty"):
        ExcelQuoteRepository(file_path)


def test_empty_phrase_raises_validation_error(tmp_path: Path):
    rows = [["author", "phrase"]]
    for i in range(99):
        rows.append([f"Author {i}", f"Phrase number {i}"])
    rows.append(["Valid Author", ""])  # Empty phrase

    file_path = create_temp_excel(tmp_path, "empty_phrase.xlsx", rows)
    with pytest.raises(DatasetValidationError, match="Row 101: phrase must be non-empty"):
        ExcelQuoteRepository(file_path)


def test_duplicate_phrase_raises_validation_error(tmp_path: Path):
    rows = [["author", "phrase"]]
    for i in range(98):
        rows.append([f"Author {i}", f"Phrase number {i}"])
    # Add duplicate phrase
    rows.append(["Author 99", "Duplicate phrase test"])
    rows.append(["Author 100", "Duplicate phrase test"])

    file_path = create_temp_excel(tmp_path, "duplicate_phrase.xlsx", rows)
    with pytest.raises(DatasetValidationError, match="duplicate phrase detected"):
        ExcelQuoteRepository(file_path)


def test_incorrect_quote_count_raises_validation_error(tmp_path: Path):
    # File with only 10 quotes instead of 100
    rows = [["author", "phrase"]]
    for i in range(10):
        rows.append([f"Author {i}", f"Phrase number {i}"])

    file_path = create_temp_excel(tmp_path, "invalid_count.xlsx", rows)
    with pytest.raises(DatasetValidationError, match="Expected exactly 100 valid quotes, but loaded 10"):
        ExcelQuoteRepository(file_path)
