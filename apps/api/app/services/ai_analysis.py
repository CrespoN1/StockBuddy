"""
Async AI analysis via DeepSeek / OpenAI.

Migrated from: ai_explainer.py (original StockBuddy)
Changes: sync requests → async httpx, errors raised as exceptions not strings,
         prompt templates preserved verbatim, retry logic added.
"""

import structlog

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = structlog.stdlib.get_logger(__name__)

SYSTEM_PROMPT = "You are a knowledgeable, unbiased investment analyst."


class AIAnalysisError(Exception):
    pass


# ─── Low-level API call ──────────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=30))
async def _call_ai_api(prompt: str, max_tokens: int | None = None) -> str:
    """Post a prompt to the configured AI service and return the response text.

    Raises AIAnalysisError on failure.
    """
    if not settings.deepseek_api_key:
        raise AIAnalysisError("Missing DEEPSEEK_API_KEY in environment.")

    max_tokens = max_tokens or settings.ai_max_tokens

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.deepseek_api_key}",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "max_tokens": max_tokens,
        "temperature": settings.ai_temperature,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(settings.deepseek_url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except (KeyError, IndexError) as exc:
        raise AIAnalysisError(f"Unexpected AI response structure: {exc}") from exc


# ─── High-level analysis methods ─────────────────────────────────────

async def explain_earnings_call(
    ticker: str,
    call_text: str,
    fundamentals: dict | None = None,
) -> str:
    """Generate comprehensive earnings call analysis.

    Prompt preserved from EnhancedAIExplainer.explain_earnings_call.
    """
    fundamentals_str = ""
    if fundamentals:
        fundamentals_str = f"""
        Company Fundamentals:
        - Sector: {fundamentals.get('sector', 'N/A')}
        - Market Cap: {fundamentals.get('market_cap', 'N/A')}
        - P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}
        - Beta: {fundamentals.get('beta', 'N/A')}
        - Dividend Yield: {fundamentals.get('dividend_yield', 'N/A')}
        """

    prompt = f"""
    You are an investment analyst. Analyze this earnings call transcript for {ticker}.

    {fundamentals_str}

    Please provide a comprehensive analysis covering:

    1. EXECUTIVE SUMMARY (3-4 bullet points)
    2. FINANCIAL PERFORMANCE (Revenue, EPS, Margins mentioned)
    3. BUSINESS HIGHLIGHTS (Key developments, new products, expansions)
    4. MANAGEMENT GUIDANCE (Future outlook, forecasts)
    5. RISK FACTORS (Challenges, competition, market risks mentioned)
    6. INVESTMENT IMPLICATIONS (What this means for investors)
    7. SENTIMENT ANALYSIS (Overall tone: Positive/Neutral/Negative)

    Focus on actionable insights. Be concise but thorough.

    EARNINGS CALL TRANSCRIPT:
    {call_text[:15000]}

    Format your response with clear sections and bullet points.
    """
    return await _call_ai_api(prompt)


async def analyze_portfolio_with_earnings(
    portfolio_data: dict,
    earnings_analyses: list[dict],
) -> str:
    """Generate portfolio-level analysis incorporating earnings insights.

    Prompt preserved from EnhancedAIExplainer.analyze_portfolio_with_earnings.
    """
    portfolio_summary = f"""
    Portfolio Overview:
    - Total Value: ${portfolio_data.get('total_value', 0):,.2f}
    - Number of Positions: {portfolio_data.get('num_positions', 0)}
    - Health Score: {portfolio_data.get('health_score', 0)}/100
    - Sector Allocation: {portfolio_data.get('sector_allocation', {})}
    """

    earnings_summary = "\nEarnings Call Insights:\n"
    for analysis in earnings_analyses:
        earnings_summary += (
            f"- {analysis.get('ticker')}: "
            f"{analysis.get('summary', 'No analysis')[:100]}...\n"
        )

    prompt = f"""
    You are a portfolio manager analyzing a stock portfolio with recent earnings call data.

    {portfolio_summary}

    Recent Earnings Analyses:
    {earnings_summary}

    Provide a comprehensive portfolio analysis covering:

    1. OVERALL PORTFOLIO HEALTH
    2. EARNINGS EXPOSURE ANALYSIS (How many holdings have recent earnings data)
    3. SECTOR CONCENTRATION RISKS
    4. EARNINGS-DRIVEN INSIGHTS (Based on the earnings calls)
    5. RECOMMENDED ACTIONS (Review, rebalance, research suggestions)
    6. RISK ASSESSMENT (Considering earnings sentiment)

    Be educational, not advisory. Suggest what an investor might discuss with a financial professional.
    """
    return await _call_ai_api(prompt)


async def compare_multiple_earnings(
    tickers: list[str],
    analyses: list[dict],
) -> str:
    """Compare earnings calls across multiple companies.

    Prompt preserved from EnhancedAIExplainer.compare_multiple_earnings,
    enhanced to include full earnings analysis summaries for richer comparison.
    """
    comparison_data = ""
    for ticker, analysis in zip(tickers, analyses):
        key_themes = analysis.get("key_themes", "")
        sentiment = analysis.get("sentiment", "Neutral")
        guidance = analysis.get("guidance", "")

        comparison_data += f"""
        === {ticker} ===
        Sentiment: {sentiment}
        Guidance Outlook: {guidance}
        Earnings Analysis Summary:
        {key_themes if key_themes else 'No earnings data available.'}
        """

    prompt = f"""
    You are an investment analyst comparing recent earnings across companies.
    Use ONLY the data provided below. Do NOT use hypothetical scenarios.
    If data is missing for a company, note it but focus analysis on companies with data.

    {comparison_data}

    Provide a detailed comparative analysis:
    1. INDUSTRY TRENDS (Common themes across these companies)
    2. RELATIVE PERFORMANCE (Which companies outperformed based on their earnings)
    3. OUTLOOK COMPARISON (Which have more positive guidance and why)
    4. RISK COMPARISON (Which face similar/different risks)
    5. INVESTMENT IMPLICATIONS (For sector/industry investors)

    Base your analysis strictly on the earnings data provided above.
    Highlight specific differences and similarities in management tone and outlook.
    """
    return await _call_ai_api(prompt)
