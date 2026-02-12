# ai_explainer.py
import os
from typing import Optional, Dict, List
from config import DEEPSEEK_API_KEY, DEEPSEEK_URL, OPENAI_API_KEY
import requests


class EnhancedAIExplainer:
    def __init__(self, use_deepseek: bool = True):
        self.use_deepseek = use_deepseek
        self.api_key = DEEPSEEK_API_KEY if use_deepseek else OPENAI_API_KEY
        self.base_url = DEEPSEEK_URL if use_deepseek else "https://api.openai.com/v1/chat/completions"

    def explain_earnings_call(self, ticker: str, call_text: str,
                              fundamentals: Optional[Dict] = None) -> str:
        """Generate comprehensive earnings call explanation"""

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
        {call_text[:15000]}  # Truncate if too long

        Format your response with clear sections and bullet points.
        """

        return self._call_ai_api(prompt)

    def analyze_portfolio_with_earnings(self, portfolio_data: Dict,
                                        earnings_analyses: List[Dict]) -> str:
        """Generate portfolio-level analysis incorporating earnings insights"""

        portfolio_summary = f"""
        Portfolio Overview:
        - Total Value: ${portfolio_data.get('total_value', 0):,.2f}
        - Number of Positions: {portfolio_data.get('num_positions', 0)}
        - Health Score: {portfolio_data.get('health_score', 0)}/100
        - Sector Allocation: {portfolio_data.get('sector_allocation', {})}
        """

        earnings_summary = "\nEarnings Call Insights:\n"
        for analysis in earnings_analyses:
            earnings_summary += f"- {analysis.get('ticker')}: {analysis.get('summary', 'No analysis')[:100]}...\n"

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

        return self._call_ai_api(prompt)

    def compare_multiple_earnings(self, tickers: List[str],
                                  analyses: List[Dict]) -> str:
        """Compare earnings calls across multiple companies"""

        comparison_data = ""
        for ticker, analysis in zip(tickers, analyses):
            comparison_data += f"""
            {ticker}:
            - Sentiment: {analysis.get('sentiment', 'Neutral')}
            - Key Themes: {analysis.get('key_themes', '')}
            - Guidance: {analysis.get('guidance', '')}
            """

        prompt = f"""
        Compare these earnings calls across companies:

        {comparison_data}

        Provide a comparative analysis:
        1. INDUSTRY TRENDS (Common themes across companies)
        2. RELATIVE PERFORMANCE (Which companies outperformed)
        3. OUTLOOK COMPARISON (Which have more positive guidance)
        4. RISK COMPARISON (Which face similar/different risks)
        5. INVESTMENT IMPLICATIONS (For sector/industry investors)

        Highlight differences and similarities in management tone and outlook.
        """

        return self._call_ai_api(prompt)

    def _call_ai_api(self, prompt: str, max_tokens: int = 2000) -> str:
        """Make API call to AI service"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": "deepseek-chat" if self.use_deepseek else "gpt-4",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a knowledgeable, unbiased investment analyst."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False,
            "max_tokens": max_tokens,
            "temperature": 0.4
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Error generating analysis: {str(e)}"