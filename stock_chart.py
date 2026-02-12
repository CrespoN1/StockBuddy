# stock_chart.py
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplfinance as mpf
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
import pandas as pd


class StockChartAnalyzer:
    def __init__(self, root):
        self.root = root
        self.fig = None
        self.canvas = None

    def fetch_stock_data(self, ticker, period="1y"):
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period=period)
            return df
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return None

    def create_candlestick_chart(self, parent, ticker, period="6mo"):
        """Create candlestick chart in a tkinter frame"""
        # Clear previous chart if exists
        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        # Fetch data
        df = self.fetch_stock_data(ticker, period)
        if df is None or df.empty:
            return None

        # Create figure
        self.fig, ax = plt.subplots(figsize=(10, 6))

        # Plot candlestick chart
        mpf.plot(df, type='candle', style='charles',
                 title=f"{ticker} - {period} Price Chart",
                 ylabel='Price ($)',
                 volume=True,
                 ax=ax,
                 returnfig=True)

        # Add moving averages
        df['MA20'] = df['Close'].rolling(window=20).mean()
        df['MA50'] = df['Close'].rolling(window=50).mean()

        ax.plot(df.index, df['MA20'], label='20-Day MA', color='orange', alpha=0.7)
        ax.plot(df.index, df['MA50'], label='50-Day MA', color='blue', alpha=0.7)
        ax.legend()

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        return df

    def get_stock_info(self, ticker):
        """Get detailed stock information"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Extract key information
            stock_details = {
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': self._format_market_cap(info.get('marketCap', 0)),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A'),
                'volume': info.get('volume', 'N/A'),
                'employees': info.get('fullTimeEmployees', 'N/A'),
                'website': info.get('website', 'N/A'),
                'summary': info.get('longBusinessSummary', 'No description available.'),
            }

            # Get institutional holders
            institutional = stock.institutional_holders
            if institutional is not None and not institutional.empty:
                stock_details['top_institutional'] = institutional.head(5).to_dict('records')

            # Get recommendations
            recommendations = stock.recommendations
            if recommendations is not None and not recommendations.empty:
                latest_rec = recommendations.iloc[-1] if len(recommendations) > 0 else None
                if latest_rec is not None:
                    stock_details['latest_recommendation'] = {
                        'firm': latest_rec.get('firm', 'N/A'),
                        'rating': latest_rec.get('toGrade', 'N/A'),
                        'action': latest_rec.get('action', 'N/A')
                    }

            return stock_details
        except Exception as e:
            print(f"Error getting stock info for {ticker}: {e}")
            return None

    def _format_market_cap(self, market_cap):
        """Format market cap to readable string"""
        if market_cap >= 1e12:
            return f"${market_cap / 1e12:.2f}T"
        elif market_cap >= 1e9:
            return f"${market_cap / 1e9:.2f}B"
        elif market_cap >= 1e6:
            return f"${market_cap / 1e6:.2f}M"
        else:
            return f"${market_cap:,.0f}"