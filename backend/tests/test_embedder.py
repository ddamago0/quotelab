import pytest
from app.infra.embeddings.local_embedder import LocalSentenceTransformerEmbedder


def test_embedder_empty_text_raises_error():
    embedder = LocalSentenceTransformerEmbedder(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    with pytest.raises(ValueError, match="cannot be empty or whitespace"):
        embedder.embed_text("")

    with pytest.raises(ValueError, match="cannot be empty or whitespace"):
        embedder.embed_text("   ")


def test_embedder_batch_empty_text_raises_error():
    embedder = LocalSentenceTransformerEmbedder(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    with pytest.raises(ValueError, match="must be non-empty strings"):
        embedder.embed_batch(["Valid text", ""])


def test_embedder_dimension_and_shape():
    """Verify paraphrase-multilingual-MiniLM-L12-v2 produces 384-dimensional dense vectors."""
    embedder = LocalSentenceTransformerEmbedder(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    vector = embedder.embed_text("El conocimiento es poder.")
    assert isinstance(vector, list)
    assert len(vector) == 384

    batch_vectors = embedder.embed_batch(["La imaginación es importante.", "El tiempo vuela."])
    assert len(batch_vectors) == 2
    assert len(batch_vectors[0]) == 384
    assert len(batch_vectors[1]) == 384
