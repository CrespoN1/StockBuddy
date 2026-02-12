"""
Parse structured sentiment data from AI earnings analysis text.

Extracts sentiment_score, guidance_outlook, risk/growth mention counts,
and key financial metrics from the sectioned AI response format.
"""

import re
import logging

logger = logging.getLogger(__name__)


def parse_analysis(text: str) -> dict:
    """Parse an AI-generated earnings analysis into structured fields.

    The AI prompt requests 7 numbered sections. This parser extracts
    structured data from those sections using pattern matching.

    Returns:
        dict with keys: sentiment_score, guidance_outlook, risk_mentions,
        growth_mentions, key_metrics
    """
    result = {
        "sentiment_score": 0.0,
        "guidance_outlook": "neutral",
        "risk_mentions": 0,
        "growth_mentions": 0,
        "key_metrics": {},
    }

    try:
        result["sentiment_score"] = _extract_sentiment_score(text)
        result["guidance_outlook"] = _extract_guidance_outlook(text)
        result["risk_mentions"] = _count_risk_mentions(text)
        result["growth_mentions"] = _count_growth_mentions(text)
        result["key_metrics"] = _extract_key_metrics(text)
    except Exception as exc:
        logger.warning("Failed to parse analysis text: %s", exc)

    return result


def _extract_section(text: str, section_num: int, section_name: str) -> str:
    """Extract text between a numbered section header and the next section."""
    pattern = rf"{section_num}\.\s*{section_name}.*?\n(.*?)(?=\d+\.\s+[A-Z]|\Z)"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _extract_sentiment_score(text: str) -> float:
    """Extract sentiment score from the SENTIMENT ANALYSIS section."""
    section = _extract_section(text, 7, "SENTIMENT ANALYSIS")
    if not section:
        # Fall back to searching the full text
        section = text

    text_lower = section.lower()

    # Look for explicit sentiment keywords
    strong_positive = ["strongly positive", "very positive", "highly positive", "bullish"]
    strong_negative = ["strongly negative", "very negative", "highly negative", "bearish"]
    positive = ["positive", "optimistic", "confident", "upbeat", "encouraging"]
    negative = ["negative", "pessimistic", "cautious", "concerning", "disappointing"]
    neutral = ["neutral", "mixed", "balanced", "moderate"]

    for phrase in strong_positive:
        if phrase in text_lower:
            return 0.8

    for phrase in strong_negative:
        if phrase in text_lower:
            return -0.8

    for phrase in positive:
        if phrase in text_lower:
            return 0.5

    for phrase in negative:
        if phrase in text_lower:
            return -0.5

    for phrase in neutral:
        if phrase in text_lower:
            return 0.0

    return 0.0


def _extract_guidance_outlook(text: str) -> str:
    """Extract guidance outlook from MANAGEMENT GUIDANCE section."""
    section = _extract_section(text, 4, "MANAGEMENT GUIDANCE")
    if not section:
        section = text

    text_lower = section.lower()

    positive_words = [
        "raised guidance", "increased outlook", "positive guidance",
        "above expectations", "strong outlook", "optimistic forecast",
        "upside", "accelerat", "raised", "exceeded",
    ]
    negative_words = [
        "lowered guidance", "reduced outlook", "negative guidance",
        "below expectations", "cautious outlook", "downside",
        "cut", "lowered", "missed", "decline",
    ]

    pos_count = sum(1 for w in positive_words if w in text_lower)
    neg_count = sum(1 for w in negative_words if w in text_lower)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    return "neutral"


def _count_risk_mentions(text: str) -> int:
    """Count risk-related keywords in RISK FACTORS section."""
    section = _extract_section(text, 5, "RISK FACTORS")
    if not section:
        return 0

    risk_keywords = [
        "risk", "challenge", "headwind", "uncertainty", "threat",
        "competition", "regulatory", "volatility", "concern", "pressure",
        "decline", "weakness", "disruption", "litigation", "debt",
    ]

    text_lower = section.lower()
    return sum(text_lower.count(kw) for kw in risk_keywords)


def _count_growth_mentions(text: str) -> int:
    """Count growth-related keywords in BUSINESS HIGHLIGHTS section."""
    section = _extract_section(text, 3, "BUSINESS HIGHLIGHTS")
    if not section:
        return 0

    growth_keywords = [
        "growth", "expansion", "new product", "innovation", "launch",
        "market share", "opportunity", "momentum", "increase", "scale",
        "revenue growth", "acquisition", "partnership", "pipeline",
    ]

    text_lower = section.lower()
    return sum(text_lower.count(kw) for kw in growth_keywords)


def _extract_key_metrics(text: str) -> dict:
    """Extract key financial metrics from FINANCIAL PERFORMANCE section."""
    section = _extract_section(text, 2, "FINANCIAL PERFORMANCE")
    if not section:
        return {}

    metrics: dict[str, str] = {}

    # Revenue patterns
    rev_match = re.search(
        r"revenue\s*(?:of\s*)?[\$]?([\d,.]+)\s*(billion|million|B|M)?",
        section, re.IGNORECASE
    )
    if rev_match:
        metrics["revenue"] = rev_match.group(0).strip()

    # EPS patterns
    eps_match = re.search(
        r"(?:EPS|earnings per share)\s*(?:of\s*)?[\$]?([\d,.]+)",
        section, re.IGNORECASE
    )
    if eps_match:
        metrics["eps"] = eps_match.group(0).strip()

    # Margin patterns
    margin_match = re.search(
        r"(?:gross|operating|net|profit)\s*margin\s*(?:of\s*)?(\d+\.?\d*)\s*%",
        section, re.IGNORECASE
    )
    if margin_match:
        metrics["margin"] = margin_match.group(0).strip()

    # YoY growth
    yoy_match = re.search(
        r"(\d+\.?\d*)\s*%\s*(?:year-over-year|YoY|y\/y)",
        section, re.IGNORECASE
    )
    if yoy_match:
        metrics["yoy_growth"] = yoy_match.group(0).strip()

    return metrics
