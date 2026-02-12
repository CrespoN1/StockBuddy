"""
Earnings call transcript fetcher using Financial Modeling Prep (FMP) API.

Replaces the original Selenium-based scraper from the Tkinter app.
"""

import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"


class TranscriptError(Exception):
    pass


async def fetch_transcript(
    ticker: str,
    year: int | None = None,
    quarter: int | None = None,
) -> str | None:
    """Fetch the latest earnings call transcript for a ticker from FMP.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL").
        year: Optional year to target a specific call.
        quarter: Optional quarter (1-4) to target a specific call.

    Returns:
        The transcript text, or None if unavailable.

    Raises:
        TranscriptError: On HTTP or API errors.
    """
    if not settings.fmp_api_key:
        logger.warning("FMP_API_KEY not configured — cannot fetch transcripts")
        return None

    params: dict[str, str | int] = {"apikey": settings.fmp_api_key}
    if year is not None:
        params["year"] = year
    if quarter is not None:
        params["quarter"] = quarter

    url = f"{FMP_BASE_URL}/earning_call_transcript/{ticker.upper()}"

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as exc:
        raise TranscriptError(
            f"FMP API returned {exc.response.status_code} for {ticker}"
        ) from exc
    except httpx.RequestError as exc:
        raise TranscriptError(f"Failed to reach FMP API: {exc}") from exc

    if not data:
        logger.info("No transcript found for %s", ticker)
        return None

    # FMP returns a list of transcripts; take the first (most recent)
    if isinstance(data, list) and len(data) > 0:
        transcript = data[0]
        content = transcript.get("content", "")
        if content:
            return content

    logger.info("Empty transcript response for %s", ticker)
    return None
