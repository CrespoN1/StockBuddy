# portfolio_analyzer.py
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import json
from models import EnhancedHolding, PortfolioSnapshot
from market_data import get_stock_fundamentals, get_latest_price
from config import DEEPSEEK_URL, DEEPSEEK_API_KEY
import requests
import uuid


class PortfolioAnalyzer:
    def __init__(self):
        self.holdings: List[EnhancedHolding] = []
        self.earnings_calls: Dict[str, List[Dict]] = {}  # ticker -> list of earnings calls

    def add_holding(self, ticker: str, shares: float = 100, portfolio_name: str = "My Portfolio") -> EnhancedHolding:
        """Add a holding to analyze"""
        holding = EnhancedHolding(
            ticker=ticker.upper(),
            shares=shares,
            portfolio_name=portfolio_name
        )

        # Get market data
        try:
            fundamentals = get_stock_fundamentals(ticker)
            holding.last_price = get_latest_price(ticker)
            holding.sector = fundamentals.get("sector")
            holding.beta = fundamentals.get("beta")
            holding.dividend_yield = fundamentals.get("dividend_yield")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            # Set defaults if API fails
            holding.last_price = 0.0
            holding.sector = "Unknown"
            holding.beta = 1.0

        self.holdings.append(holding)
        self.earnings_calls[ticker.upper()] = []  # Initialize empty list for earnings calls
        return holding

    def add_earnings_call(self, ticker: str, call_text: str, summary: str,
                          sentiment_score: float = 0.0) -> None:
        """Add an earnings call analysis for a holding"""
        ticker = ticker.upper()

        earnings_call = {
            "id": str(uuid.uuid4()),
            "ticker": ticker,
            "call_text": call_text[:5000] if len(call_text) > 5000 else call_text,  # Truncate if too long
            "summary": summary,
            "sentiment_score": sentiment_score,
            "created_at": datetime.now().isoformat()
        }

        if ticker in self.earnings_calls:
            self.earnings_calls[ticker].append(earnings_call)
        else:
            self.earnings_calls[ticker] = [earnings_call]

        # Update the holding with the latest earnings info
        for holding in self.holdings:
            if holding.ticker == ticker:
                holding.latest_earnings_call = datetime.now()
                holding.earnings_call_summary = summary
                # Store sentiment as a custom attribute
                holding.sentiment_score = sentiment_score
                break

    def get_earnings_for_ticker(self, ticker: str) -> List[Dict]:
        """Get earnings calls for a specific ticker"""
        return self.earnings_calls.get(ticker.upper(), [])

    def analyze_portfolio(self) -> PortfolioSnapshot:
        """Analyze the entire portfolio"""
        if not self.holdings:
            return PortfolioSnapshot(
                portfolio_name="Empty Portfolio",
                num_positions=0,
                health_score=0
            )

        # Calculate values
        total_value = 0.0
        for holding in self.holdings:
            if holding.last_price and holding.shares:
                total_value += holding.last_price * holding.shares

        # Calculate weights and concentration
        weights = []
        holding_values = []

        for holding in self.holdings:
            if holding.last_price and holding.shares:
                value = holding.last_price * holding.shares
                weight = value / total_value if total_value > 0 else 0
                weights.append(weight)
                holding_values.append(value)

        concentration_risk = max(weights) if weights else 0

        # Calculate sentiment from earnings calls
        sentiment_scores = []
        earnings_coverage = 0

        for holding in self.holdings:
            # Check if we have sentiment_score attribute (from earnings calls)
            if hasattr(holding, 'sentiment_score') and holding.sentiment_score is not None:
                sentiment_scores.append(holding.sentiment_score)
                earnings_coverage += 1

        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        recent_earnings_coverage = earnings_coverage / len(self.holdings) if self.holdings else 0

        # Calculate health score
        health_score = self._calculate_health_score(
            concentration_risk=concentration_risk,
            num_positions=len(self.holdings),
            avg_sentiment=avg_sentiment,
            total_value=total_value
        )

        snapshot = PortfolioSnapshot(
            portfolio_name=f"Portfolio Analysis {datetime.now().strftime('%Y-%m-%d')}",
            total_value=total_value,
            num_positions=len(self.holdings),
            recent_earnings_coverage=recent_earnings_coverage,
            avg_sentiment_score=avg_sentiment if sentiment_scores else None,
            concentration_risk=concentration_risk,
            health_score=health_score
        )

        return snapshot

    def get_sector_allocation(self) -> Dict[str, float]:
        """Calculate sector allocation"""
        sector_totals = {}
        total_value = sum(
            h.last_price * h.shares
            for h in self.holdings
            if h.last_price and h.shares
        )

        if total_value == 0:
            return {}

        for holding in self.holdings:
            if holding.last_price and holding.shares:
                value = holding.last_price * holding.shares
                weight = value / total_value
                sector = holding.sector or "Unknown"
                sector_totals[sector] = sector_totals.get(sector, 0) + weight

        return sector_totals

    def get_earnings_insights(self) -> Dict:
        """Get insights based on earnings calls"""
        insights = {
            "holdings_with_recent_earnings": [],
            "positive_outlooks": [],
            "risk_warnings": [],
            "recommended_reviews": [],
            "sentiment_summary": {
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "no_data": 0
            }
        }

        for holding in self.holdings:
            ticker = holding.ticker
            earnings_calls = self.earnings_calls.get(ticker, [])

            if earnings_calls:
                insights["holdings_with_recent_earnings"].append(ticker)

                # Get latest sentiment
                latest_call = earnings_calls[-1]  # Most recent
                sentiment = latest_call.get("sentiment_score", 0)

                # Categorize sentiment
                if sentiment > 0.2:
                    insights["positive_outlooks"].append(ticker)
                    insights["sentiment_summary"]["positive"] += 1
                elif sentiment < -0.1:
                    insights["risk_warnings"].append(ticker)
                    insights["sentiment_summary"]["negative"] += 1
                else:
                    insights["sentiment_summary"]["neutral"] += 1
            else:
                insights["sentiment_summary"]["no_data"] += 1

        return insights

    def _calculate_health_score(self, concentration_risk: float,
                                num_positions: int, avg_sentiment: float,
                                total_value: float) -> int:
        """Calculate portfolio health score 0-100"""
        score = 100

        # Concentration penalty
        if concentration_risk > 0.35:
            score -= 30
        elif concentration_risk > 0.25:
            score -= 20
        elif concentration_risk > 0.15:
            score -= 10

        # Position count
        if num_positions < 5:
            score -= 15
        elif num_positions < 10:
            score -= 5

        # Sentiment bonus/penalty
        if avg_sentiment > 0.3:
            score += 10
        elif avg_sentiment < -0.2:
            score -= 15

        # Value bonus (larger portfolios get small bonus)
        if total_value > 100000:
            score += 5
        elif total_value < 10000:
            score -= 5

        return max(0, min(100, score))

    def get_earnings_insights(self) -> Dict:
        """Get insights based on earnings calls"""
        insights = {
            "holdings_with_recent_earnings": [],
            "positive_outlooks": [],
            "risk_warnings": [],
            "recommended_reviews": []
        }

        for holding in self.holdings:
            # Check if we have recent earnings analysis
            if hasattr(holding, 'latest_earnings_call'):
                insights["holdings_with_recent_earnings"].append(holding.ticker)

                if hasattr(holding, 'sentiment_score') and holding.sentiment_score:
                    if holding.sentiment_score > 0.3:
                        insights["positive_outlooks"].append(holding.ticker)
                    elif holding.sentiment_score < -0.1:
                        insights["risk_warnings"].append(holding.ticker)

            # Check if earnings date is coming up
            if hasattr(holding, 'next_earnings_date'):
                if holding.next_earnings_date:
                    earnings_date = datetime.strptime(holding.next_earnings_date, "%Y-%m-%d")
                    if earnings_date - datetime.now() < timedelta(days=30):
                        insights["recommended_reviews"].append(holding.ticker)

        return insights

    def get_holdings_without_earnings(self) -> List[str]:
        """Get list of holdings without earnings call analysis"""
        holdings_without = []
        for holding in self.holdings:
            ticker = holding.ticker
            if ticker not in self.earnings_calls or not self.earnings_calls[ticker]:
                holdings_without.append(ticker)
        return holdings_without

    def clear_portfolio(self) -> None:
        """Clear all holdings and earnings data"""
        self.holdings.clear()
        self.earnings_calls.clear()