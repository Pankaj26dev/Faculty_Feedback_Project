try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except Exception:
    SentimentIntensityAnalyzer = None

_analyzer = SentimentIntensityAnalyzer() if SentimentIntensityAnalyzer is not None else None

__all__ = ["analyze_sentiment"]


def analyze_sentiment(text: str) -> str:
    """Return sentiment label for the given text: 'Positive', 'Neutral', or 'Negative'.

    Uses VADER when available; otherwise falls back to a simple keyword heuristic so
    the function works without external dependencies during early development.
    """
    if not text:
        return "Neutral"

    text = str(text)

    if _analyzer is not None:
        scores = _analyzer.polarity_scores(text)
        compound = scores.get("compound", 0.0)
        if compound >= 0.05:
            return "Positive"
        if compound <= -0.05:
            return "Negative"
        return "Neutral"

    # Simple fallback heuristic
    text_l = text.lower()
    positive_keywords = [
        "good",
        "great",
        "excellent",
        "love",
        "loved",
        "nice",
        "helpful",
        "clear",
        "well",
        "best",
        "enjoyed",
        "understand",
    ]
    negative_keywords = [
        "bad",
        "terrible",
        "poor",
        "hate",
        "hated",
        "slow",
        "confusing",
        "difficult",
        "boring",
        "hard",
        "worse",
    ]

    pos = sum(text_l.count(k) for k in positive_keywords)
    neg = sum(text_l.count(k) for k in negative_keywords)

    if pos > neg:
        return "Positive"
    if neg > pos:
        return "Negative"
    return "Neutral"
