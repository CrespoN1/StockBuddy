"""
Stock news fetcher using Alpha Vantage NEWS_SENTIMENT endpoint.

Provides news articles with sentiment scores for individual tickers.
"""

import structlog
import httpx

from app.config import settings

logger = structlog.stdlib.get_logger(__name__)


class NewsError(Exception):
    pass


async def get_stock_news(
    ticker: str,
    limit: int = 10,
) -> list[dict]:
    """Fetch recent news articles with sentiment for a ticker.

    Uses Alpha Vantage NEWS_SENTIMENT function (available on free tier).

    Returns list of dicts with keys: title, url, source, published_at,
    summary, sentiment_score, sentiment_label, relevance_score.
    """
    if not settings.alpha_vantage_api_key:
        logger.warning("ALPHA_VANTAGE_API_KEY not set — cannot fetch news")
        return []

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                settings.alpha_vantage_base_url,
                params={
                    "function": "NEWS_SENTIMENT",
                    "tickers": ticker.upper(),
                    "limit": min(limit, 50),
                    "apikey": settings.alpha_vantage_api_key,
                },
            )

            if resp.status_code != 200:
                logger.warning("News API returned status %d", resp.status_code)
                return []

            data = resp.json()

            # Check for rate limit / error messages
            if "Note" in data or "Information" in data:
                logger.warning(
                    "Alpha Vantage news rate limit: %s",
                    data.get("Note") or data.get("Information"),
                )
                return []

            feed = data.get("feed", [])
            articles = []

            for item in feed[:limit]:
                # Find ticker-specific sentiment from the item
                ticker_sentiment = _extract_ticker_sentiment(item, ticker.upper())

                articles.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "source": item.get("source", ""),
                    "published_at": item.get("time_published", ""),
                    "summary": item.get("summary", ""),
                    "banner_image": item.get("banner_image", ""),
                    "overall_sentiment_score": _safe_float(
                        item.get("overall_sentiment_score")
                    ),
                    "overall_sentiment_label": item.get(
                        "overall_sentiment_label", ""
                    ),
                    "ticker_sentiment_score": ticker_sentiment.get("score", 0.0),
                    "ticker_sentiment_label": ticker_sentiment.get("label", "Neutral"),
                    "ticker_relevance": ticker_sentiment.get("relevance", 0.0),
                })

            return articles

    except httpx.RequestError as exc:
        logger.warning("Failed to fetch news for %s: %s", ticker, exc)
        return []
    except Exception as exc:
        logger.warning("Unexpected error fetching news for %s: %s", ticker, exc)
        return []


def _extract_ticker_sentiment(item: dict, ticker: str) -> dict:
    """Extract ticker-specific sentiment from news item."""
    for ts in item.get("ticker_sentiment", []):
        if ts.get("ticker", "").upper() == ticker:
            return {
                "score": _safe_float(ts.get("ticker_sentiment_score")),
                "label": ts.get("ticker_sentiment_label", "Neutral"),
                "relevance": _safe_float(ts.get("relevance_score")),
            }
    return {"score": 0.0, "label": "Neutral", "relevance": 0.0}


def _safe_float(value) -> float:
    """Safely convert to float."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0
