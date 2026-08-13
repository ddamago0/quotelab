import pytest
from app.infra.tokenizer.local_tokenizer import LocalTokenizer


def test_tokenizer_empty_and_whitespace():
    tokenizer = LocalTokenizer()
    assert tokenizer.count_units("") == 0
    assert tokenizer.count_units("   ") == 0


def test_tokenizer_single_words_and_phrases():
    tokenizer = LocalTokenizer()
    assert tokenizer.count_units("Hola") == 1
    assert tokenizer.count_units("La libertad es importante.") == 4
    assert tokenizer.count_units("  Tres  palabras  separadas  ") == 3


def test_tokenizer_deterministic_consistency():
    tokenizer = LocalTokenizer()
    text = "El éxito consiste en obtener lo que se desea. La felicidad, en disfrutar lo que se obtiene."
    count1 = tokenizer.count_units(text)
    count2 = tokenizer.count_units(text)
    assert count1 == count2
    assert count1 == 17

