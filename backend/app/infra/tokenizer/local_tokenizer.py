from app.domain.ports import TokenizerPort


class LocalTokenizer(TokenizerPort):
    """
    Concrete implementation of TokenizerPort for deterministic text unit / token counting.
    Calculates whitespace-delimited word tokens without external API or network dependencies.
    """

    def count_units(self, text: str) -> int:
        """
        Calculates token or text-unit count for a given text string.
        Returns 0 for empty or whitespace-only text.
        """
        if not text or not text.strip():
            return 0
        return len(text.strip().split())
