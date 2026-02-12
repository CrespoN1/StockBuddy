# main.py - Enhanced GUI Application
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime
import json
from stock_chart import StockChartAnalyzer
import yfinance as yf
import pandas as pd

from config import MASSIVE_API_KEY, MASSIVE_BASE_URL
from market_data import get_stock_fundamentals, get_latest_price
from portfolio_analyzer import PortfolioAnalyzer
from ai_explainer import EnhancedAIExplainer
from models import EnhancedHolding

# Selenium imports (for web scraping)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import requests


class EnhancedEarningsAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Portfolio & Earnings Call Analyzer")
        self.root.geometry("1200x900")  # Increased size for deep-dive

        # Initialize components
        self.portfolio_analyzer = PortfolioAnalyzer()
        self.ai_explainer = EnhancedAIExplainer()
        self.chart_analyzer = StockChartAnalyzer(root)  # Add chart analyzer
        self.current_holdings = []

        # Setup Selenium
        self.setup_selenium()

        # Setup GUI
        self.setup_gui()

        # Store current deep-dive ticker
        self.current_deep_dive_ticker = None

    def setup_selenium(self):
        """Setup Selenium for web scraping"""
        try:
            self.service = Service("chromedriver.exe")
            self.options = Options()
            self.options.add_argument("--headless")  # Run in background
            self.options.add_argument("--disable-gpu")
            self.options.add_argument("--no-sandbox")
            self.driver = webdriver.Chrome(service=self.service, options=self.options)
        except Exception as e:
            print(f"Selenium setup failed: {e}")
            self.driver = None

    def setup_gui(self):
        """Setup the enhanced GUI"""
        # Create Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Tab 1: Earnings Call Analysis (original functionality)
        self.setup_earnings_tab()

        # Tab 2: Portfolio Management (new features)
        self.setup_portfolio_tab()

        # Tab 3: Comparative Analysis
        self.setup_comparison_tab()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.loading_frame = ttk.Frame(self.root)
        self.loading_label = ttk.Label(self.loading_frame, text="")
        self.loading_progress = ttk.Progressbar(self.loading_frame, mode='indeterminate', length=200)
        self.loading_label.pack(side=tk.LEFT, padx=5)
        self.loading_progress.pack(side=tk.LEFT, padx=5)
        self.loading_frame.pack_forget()

    def disable_buttons_during_operation(self, disable=True):
        """Disable/enable action buttons during long operations"""
        state = "disabled" if disable else "normal"

        # Try to disable common buttons if they exist
        button_attributes = [
            'search_button',  # Search tickers button
            'analyze_button',  # Analyze earnings call button
            'add_holding_button',  # Add holding button
            'portfolio_analyze_button',  # Analyze portfolio button
            'compare_button',  # Compare earnings button
            'clear_button',  # Clear results button
            'export_button',  # Export button
            'load_sample_button',  # Load sample button
            'clear_portfolio_button',  # Clear portfolio button
        ]

        for attr_name in button_attributes:
            if hasattr(self, attr_name):
                button = getattr(self, attr_name)
                if button and hasattr(button, 'config'):
                    try:
                        button.config(state=state)
                    except:
                        pass

    def setup_earnings_tab(self):
        """Setup earnings call analysis tab (enhanced version of original)"""
        earnings_frame = ttk.Frame(self.notebook)
        self.notebook.add(earnings_frame, text="Earnings Call Analysis")

        # Search Section
        search_frame = ttk.LabelFrame(earnings_frame, text="Search & Select Company", padding="10")
        search_frame.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(search_frame, text="Ticker / Company Name:").grid(row=0, column=0, sticky=tk.W)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5)

        ttk.Button(search_frame, text="Search", command=self.search_tickers).grid(row=0, column=2, padx=5)

        # Results dropdown
        ttk.Label(search_frame, text="Select:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.ticker_combobox = ttk.Combobox(search_frame, state="readonly", width=50)
        self.ticker_combobox.grid(row=1, column=1, columnspan=2, pady=5, sticky=tk.W + tk.E)
        self.ticker_combobox.bind("<<ComboboxSelected>>", self.on_ticker_selected)

        self.selected_label = ttk.Label(search_frame, text="Selected: None")
        self.selected_label.grid(row=2, column=0, columnspan=3, sticky=tk.W, pady=5)

        # Analysis Options
        options_frame = ttk.LabelFrame(earnings_frame, text="Analysis Options", padding="10")
        options_frame.pack(fill=tk.X, pady=5, padx=5)

        self.include_fundamentals = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Include Company Fundamentals",
                        variable=self.include_fundamentals).pack(anchor=tk.W)

        self.save_to_portfolio = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Save to Portfolio for Comparison",
                        variable=self.save_to_portfolio).pack(anchor=tk.W, pady=5)

        # Action Buttons
        button_frame = ttk.Frame(earnings_frame)
        button_frame.pack(fill=tk.X, pady=10, padx=5)

        ttk.Button(button_frame, text="Analyze Earnings Call",
                   command=self.analyze_earnings_call).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Results",
                   command=self.clear_results).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Analysis",
                   command=self.export_analysis).pack(side=tk.LEFT, padx=5)

        # Results Display
        results_frame = ttk.LabelFrame(earnings_frame, text="AI Analysis Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD,
                                                      width=100, height=25)
        self.results_text.pack(fill=tk.BOTH, expand=True)

        # Store dropdown values
        self.dropdown_values = []

    def setup_portfolio_tab(self):
        """Setup portfolio management tab"""
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="Portfolio Management")

        paned = ttk.PanedWindow(portfolio_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left pane - Portfolio controls and holdings
        left_pane = ttk.Frame(paned)
        paned.add(left_pane, weight=1)

        # Right pane - Deep dive analysis (initially empty)
        self.right_pane = ttk.Frame(paned)
        paned.add(self.right_pane, weight=2)

        # Portfolio Controls
        control_frame = ttk.LabelFrame(portfolio_frame, text="Portfolio Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=5, padx=5)

        # Portfolio name
        ttk.Label(control_frame, text="Portfolio Name:").grid(row=0, column=0, sticky=tk.W)
        self.portfolio_name = ttk.Entry(control_frame, width=30)
        self.portfolio_name.grid(row=0, column=1, padx=5)
        self.portfolio_name.insert(0, "My Investment Portfolio")

        # Add holding section
        add_frame = ttk.LabelFrame(control_frame, text="Add Holding", padding="5")
        add_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=tk.W + tk.E)

        ttk.Label(add_frame, text="Ticker:").grid(row=0, column=0, sticky=tk.W)
        self.holding_ticker = ttk.Entry(add_frame, width=15)
        self.holding_ticker.grid(row=0, column=1, padx=5)

        ttk.Label(add_frame, text="Shares:").grid(row=0, column=2, sticky=tk.W, padx=10)
        self.holding_shares = ttk.Entry(add_frame, width=10)
        self.holding_shares.grid(row=0, column=3, padx=5)
        self.holding_shares.insert(0, "100")

        ttk.Button(add_frame, text="Add to Portfolio",
                   command=self.add_holding_to_portfolio).grid(row=0, column=4, padx=10)

        # Portfolio Actions
        action_frame = ttk.Frame(control_frame)
        action_frame.grid(row=2, column=0, columnspan=3, pady=10)

        ttk.Button(action_frame, text="Analyze Portfolio",
                   command=self.analyze_portfolio).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Clear Portfolio",
                   command=self.clear_portfolio).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Load Sample Portfolio",
                   command=self.load_sample_portfolio).pack(side=tk.LEFT, padx=5)

        # Holdings Display
        holdings_frame = ttk.LabelFrame(portfolio_frame, text="Current Holdings", padding="10")
        holdings_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        # Treeview for holdings
        columns = ("Ticker", "Shares", "Price", "Value", "Sector", "Beta", "Earnings")
        self.holdings_tree = ttk.Treeview(holdings_frame, columns=columns, show="headings", height=10)

        for col in columns:
            self.holdings_tree.heading(col, text=col)
            self.holdings_tree.column(col, width=100)

        scrollbar = ttk.Scrollbar(holdings_frame, orient=tk.VERTICAL, command=self.holdings_tree.yview)
        self.holdings_tree.configure(yscrollcommand=scrollbar.set)

        self.holdings_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = ttk.Frame(left_pane)
        button_frame.pack(fill=tk.X, pady=10)

        self.deep_dive_button = ttk.Button(
            button_frame,
            text="Deep Dive Analysis",
            command=self.show_deep_dive,
            state="disabled"  # Disabled until a holding is selected
        )
        self.deep_dive_button.pack(side=tk.LEFT, padx=5)

        # Bind selection event to holdings tree
        if hasattr(self, 'holdings_tree'):
            self.holdings_tree.bind('<<TreeviewSelect>>', self.on_holding_selected)

        # Portfolio Analysis Results
        analysis_frame = ttk.LabelFrame(portfolio_frame, text="Portfolio Analysis", padding="10")
        analysis_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.portfolio_text = scrolledtext.ScrolledText(analysis_frame, wrap=tk.WORD,
                                                        width=100, height=15)
        self.portfolio_text.pack(fill=tk.BOTH, expand=True)

    def on_holding_selected(self, event):
        """Handle selection of a holding in the treeview"""
        selection = self.holdings_tree.selection()
        if selection:
            item = self.holdings_tree.item(selection[0])
            values = item['values']
            if values:
                ticker = values[0]  # First column is ticker
                self.current_deep_dive_ticker = ticker
                self.deep_dive_button.config(state="normal")
                self.status_var.set(f"Selected: {ticker} - Click 'Deep Dive' for detailed analysis")

    def show_deep_dive(self):
        """Show deep dive analysis for selected ticker"""
        if not self.current_deep_dive_ticker:
            messagebox.showinfo("No Selection", "Please select a holding from the portfolio first.")
            return

        # Clear right pane
        for widget in self.right_pane.winfo_children():
            widget.destroy()

        ticker = self.current_deep_dive_ticker
        self.status_var.set(f"Loading deep dive analysis for {ticker}...")

        # Create notebook for deep dive tabs
        deep_dive_notebook = ttk.Notebook(self.right_pane)
        deep_dive_notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Stock Chart
        chart_frame = ttk.Frame(deep_dive_notebook)
        deep_dive_notebook.add(chart_frame, text="Price Chart")

        # Add chart controls
        chart_controls = ttk.Frame(chart_frame)
        chart_controls.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(chart_controls, text="Time Period:").pack(side=tk.LEFT, padx=5)

        self.chart_period = tk.StringVar(value="6mo")
        periods = ["1mo", "3mo", "6mo", "1y", "2y", "5y"]
        period_menu = ttk.OptionMenu(chart_controls, self.chart_period, "6mo", *periods)
        period_menu.pack(side=tk.LEFT, padx=5)

        update_chart_btn = ttk.Button(
            chart_controls,
            text="Update Chart",
            command=lambda: self.update_stock_chart(ticker, chart_display_frame)
        )
        update_chart_btn.pack(side=tk.LEFT, padx=5)

        # Frame for chart display
        chart_display_frame = ttk.Frame(chart_frame)
        chart_display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Initial chart
        self.update_stock_chart(ticker, chart_display_frame)

        # Tab 2: Company Details
        details_frame = ttk.Frame(deep_dive_notebook)
        deep_dive_notebook.add(details_frame, text="Company Details")

        # Load company details
        self.load_company_details(ticker, details_frame)

        # Tab 3: Advanced Analysis
        analysis_frame = ttk.Frame(deep_dive_notebook)
        deep_dive_notebook.add(analysis_frame, text="Advanced Analysis")

        self.setup_advanced_analysis(ticker, analysis_frame)

        self.status_var.set(f"Deep dive analysis loaded for {ticker}")

    def update_stock_chart(self, ticker, parent_frame):
        """Update stock chart with selected period"""
        # Clear previous chart
        for widget in parent_frame.winfo_children():
            widget.destroy()

        period = self.chart_period.get()

        # Show loading
        loading_label = ttk.Label(parent_frame, text=f"Loading {ticker} chart...")
        loading_label.pack(pady=50)
        parent_frame.update()

        # Create chart
        try:
            df = self.chart_analyzer.create_candlestick_chart(parent_frame, ticker, period)
            if df is not None:
                # Add basic stats
                stats_frame = ttk.Frame(parent_frame)
                stats_frame.pack(fill=tk.X, padx=10, pady=5)

                current_price = df['Close'].iloc[-1] if not df.empty else 0
                prev_close = df['Close'].iloc[-2] if len(df) > 1 else current_price
                change = current_price - prev_close
                change_pct = (change / prev_close * 100) if prev_close != 0 else 0

                ttk.Label(stats_frame, text=f"Current: ${current_price:.2f}",
                          font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=10)
                color = "green" if change >= 0 else "red"
                ttk.Label(stats_frame, text=f"Change: ${change:.2f} ({change_pct:.2f}%)",
                          foreground=color).pack(side=tk.LEFT, padx=10)

                # Add additional metrics
                if len(df) >= 20:
                    ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
                    ttk.Label(stats_frame, text=f"20-Day MA: ${ma20:.2f}").pack(side=tk.LEFT, padx=10)

        except Exception as e:
            ttk.Label(parent_frame, text=f"Error loading chart: {str(e)}",
                      foreground="red").pack(pady=20)
        finally:
            # Remove loading label if it exists
            for widget in parent_frame.winfo_children():
                if isinstance(widget, ttk.Label) and "Loading" in widget.cget("text"):
                    widget.destroy()

    def load_company_details(self, ticker, parent_frame):
        """Load company details into frame"""
        # Show loading
        loading_label = ttk.Label(parent_frame, text=f"Loading company details for {ticker}...")
        loading_label.pack(pady=50)
        parent_frame.update()

        # Create scrolled frame for details
        canvas = tk.Canvas(parent_frame)
        scrollbar = ttk.Scrollbar(parent_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        try:
            # Get stock info
            details = self.chart_analyzer.get_stock_info(ticker)

            if details:
                # Create details display
                ttk.Label(scrollable_frame, text=f"{details['name']} ({ticker})",
                          font=('Arial', 14, 'bold')).pack(anchor=tk.W, pady=10, padx=10)

                # Sector and Industry
                info_frame = ttk.LabelFrame(scrollable_frame, text="Company Information", padding=10)
                info_frame.pack(fill=tk.X, padx=10, pady=5)

                rows = [
                    ("Sector", details['sector']),
                    ("Industry", details['industry']),
                    ("Market Cap", details['market_cap']),
                    ("P/E Ratio", details['pe_ratio']),
                    ("Forward P/E", details['forward_pe']),
                    ("Dividend Yield",
                     f"{float(details['dividend_yield']) * 100:.2f}%" if details['dividend_yield'] != 'N/A' else 'N/A'),
                    ("Beta", details['beta']),
                    ("52-Week High", f"${details['52_week_high']}" if details['52_week_high'] != 'N/A' else 'N/A'),
                    ("52-Week Low", f"${details['52_week_low']}" if details['52_week_low'] != 'N/A' else 'N/A'),
                    ("Avg Volume", f"{details['avg_volume']:,.0f}" if details['avg_volume'] != 'N/A' else 'N/A'),
                ]

                for label, value in rows:
                    frame = ttk.Frame(info_frame)
                    frame.pack(fill=tk.X, pady=2)
                    ttk.Label(frame, text=f"{label}:", width=15, anchor=tk.W).pack(side=tk.LEFT)
                    ttk.Label(frame, text=value, anchor=tk.W).pack(side=tk.LEFT)

                # Business Summary
                if details['summary'] != 'No description available.':
                    summary_frame = ttk.LabelFrame(scrollable_frame, text="Business Summary", padding=10)
                    summary_frame.pack(fill=tk.X, padx=10, pady=5)

                    summary_text = tk.Text(summary_frame, height=8, wrap=tk.WORD, font=('Arial', 9))
                    summary_text.insert(1.0, details['summary'])
                    summary_text.config(state="disabled")
                    summary_text.pack(fill=tk.BOTH, expand=True)

                # Website link
                if details['website'] != 'N/A':
                    website_frame = ttk.Frame(scrollable_frame)
                    website_frame.pack(fill=tk.X, padx=10, pady=5)
                    ttk.Label(website_frame, text="Website:").pack(side=tk.LEFT, padx=5)

                    def open_website(url=details['website']):
                        import webbrowser
                        webbrowser.open(url)

                    website_btn = ttk.Button(website_frame, text=details['website'],
                                             command=open_website)
                    website_btn.pack(side=tk.LEFT)

            else:
                ttk.Label(scrollable_frame, text="Could not load company details",
                          foreground="red").pack(pady=20)

        except Exception as e:
            ttk.Label(scrollable_frame, text=f"Error loading details: {str(e)}",
                      foreground="red").pack(pady=20)
        finally:
            # Pack canvas and scrollbar
            canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

            # Remove loading label
            loading_label.destroy()

    def setup_advanced_analysis(self, ticker, parent_frame):
        """Setup advanced analysis options"""
        # Analysis options frame
        options_frame = ttk.LabelFrame(parent_frame, text="Analysis Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=10)

        # Technical Analysis Button
        ttk.Button(options_frame, text="Technical Analysis",
                   command=lambda: self.run_technical_analysis(ticker)).pack(pady=5)

        # Fundamental Analysis Button
        ttk.Button(options_frame, text="Fundamental Analysis",
                   command=lambda: self.run_fundamental_analysis(ticker)).pack(pady=5)

        # Earnings Analysis Button
        ttk.Button(options_frame, text="Earnings Call Analysis",
                   command=lambda: self.analyze_single_earnings(ticker)).pack(pady=5)

        # Comparison Analysis Button
        ttk.Button(options_frame, text="Compare with Peers",
                   command=lambda: self.compare_with_peers(ticker)).pack(pady=5)

        # Results area
        self.advanced_results = scrolledtext.ScrolledText(parent_frame, wrap=tk.WORD, height=15)
        self.advanced_results.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Initialize with message
        self.advanced_results.insert(tk.END, f"Select an analysis option for {ticker}\n\n")

    def run_technical_analysis(self, ticker):
        """Run technical analysis on selected stock"""
        self.show_loading(f"Running technical analysis for {ticker}...")
        self.disable_buttons_during_operation(True)

        thread = threading.Thread(target=self._run_technical_analysis_thread, args=(ticker,))
        thread.daemon = True
        thread.start()

    def _run_technical_analysis_thread(self, ticker):
        """Thread for technical analysis"""
        try:
            # Fetch data
            df = self.chart_analyzer.fetch_stock_data(ticker, "1y")

            if df is None or df.empty:
                self.root.after(0, lambda: self.advanced_results.insert(
                    tk.END, f"Could not fetch data for {ticker}\n"))
                return

            # Calculate indicators
            analysis_text = f"=== TECHNICAL ANALYSIS: {ticker} ===\n\n"

            # Price statistics
            current_price = df['Close'].iloc[-1]
            analysis_text += f"Current Price: ${current_price:.2f}\n"

            # Moving averages
            ma20 = df['Close'].rolling(window=20).mean().iloc[-1]
            ma50 = df['Close'].rolling(window=50).mean().iloc[-1]
            ma200 = df['Close'].rolling(window=200).mean().iloc[-1]

            analysis_text += f"\nMoving Averages:\n"
            analysis_text += f"  20-Day MA: ${ma20:.2f} ({'Above' if current_price > ma20 else 'Below'} price)\n"
            analysis_text += f"  50-Day MA: ${ma50:.2f} ({'Above' if current_price > ma50 else 'Below'} price)\n"
            analysis_text += f"  200-Day MA: ${ma200:.2f} ({'Above' if current_price > ma200 else 'Below'} price)\n"

            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1])) if not pd.isna(rs.iloc[-1]) else 50

            analysis_text += f"\nRSI (14-day): {rsi:.1f} "
            if rsi > 70:
                analysis_text += "(Overbought)\n"
            elif rsi < 30:
                analysis_text += "(Oversold)\n"
            else:
                analysis_text += "(Neutral)\n"

            # Volume analysis
            avg_volume = df['Volume'].mean()
            current_volume = df['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

            analysis_text += f"\nVolume Analysis:\n"
            analysis_text += f"  Current Volume: {current_volume:,.0f}\n"
            analysis_text += f"  Average Volume: {avg_volume:,.0f}\n"
            analysis_text += f"  Volume Ratio: {volume_ratio:.1f}x average\n"

            # Support and Resistance
            recent_low = df['Low'].tail(20).min()
            recent_high = df['High'].tail(20).max()

            analysis_text += f"\nRecent Range (20 days):\n"
            analysis_text += f"  Support: ${recent_low:.2f}\n"
            analysis_text += f"  Resistance: ${recent_high:.2f}\n"

            # Add AI interpretation
            analysis_text += f"\n=== AI INTERPRETATION ===\n"

            # Generate AI analysis
            prompt = f"""
            Based on this technical analysis for {ticker}:
            - Current Price: ${current_price:.2f}
            - Relative to MAs: Above/Below 20, 50, 200-day averages
            - RSI: {rsi:.1f} ({'Overbought' if rsi > 70 else 'Oversold' if rsi < 30 else 'Neutral'})
            - Volume: {volume_ratio:.1f}x average
            - Support: ${recent_low:.2f}, Resistance: ${recent_high:.2f}

            Provide a brief (3-4 sentence) technical assessment.
            """

            ai_analysis = self.ai_explainer._call_ai_api(prompt)
            analysis_text += ai_analysis

            # Display results
            self.root.after(0, lambda: self.display_advanced_results(analysis_text))

        except Exception as e:
            self.root.after(0, lambda: self.advanced_results.insert(
                tk.END, f"Error in technical analysis: {str(e)}\n"))
        finally:
            self.root.after(0, self.hide_loading)
            self.root.after(0, lambda: self.disable_buttons_during_operation(False))

    def display_advanced_results(self, text):
        """Display results in advanced analysis text area"""
        self.advanced_results.delete(1.0, tk.END)
        self.advanced_results.insert(tk.END, text)

    def analyze_single_earnings(self, ticker):
        """Analyze earnings for the selected ticker"""
        self.current_ticker = ticker
        self.analyze_earnings_call()

    def compare_with_peers(self, ticker):
        """Compare selected stock with sector peers"""
        self.show_loading(f"Finding peers for {ticker}...")

        # This would require additional implementation
        # For now, show a placeholder
        self.root.after(0, lambda: self.advanced_results.insert(
            tk.END, f"Peer comparison for {ticker} would be implemented here.\n"))
        self.root.after(0, self.hide_loading)

    def setup_comparison_tab(self):
        """Setup comparative analysis tab"""
        comparison_frame = ttk.Frame(self.notebook)
        self.notebook.add(comparison_frame, text="Comparative Analysis")

        # Comparison Controls
        control_frame = ttk.LabelFrame(comparison_frame, text="Comparison Controls", padding="10")
        control_frame.pack(fill=tk.X, pady=5, padx=5)

        ttk.Label(control_frame, text="Select tickers to compare:").pack(anchor=tk.W)

        # Ticker selection
        ticker_frame = ttk.Frame(control_frame)
        ticker_frame.pack(fill=tk.X, pady=5)

        self.comp_ticker1 = ttk.Entry(ticker_frame, width=10)
        self.comp_ticker1.pack(side=tk.LEFT, padx=5)
        self.comp_ticker1.insert(0, "AAPL")

        self.comp_ticker2 = ttk.Entry(ticker_frame, width=10)
        self.comp_ticker2.pack(side=tk.LEFT, padx=5)
        self.comp_ticker2.insert(0, "MSFT")

        self.comp_ticker3 = ttk.Entry(ticker_frame, width=10)
        self.comp_ticker3.pack(side=tk.LEFT, padx=5)
        self.comp_ticker3.insert(0, "GOOGL")

        ttk.Button(control_frame, text="Compare Earnings Calls",
                   command=self.compare_earnings_calls).pack(pady=10)

        # Comparison Results
        results_frame = ttk.LabelFrame(comparison_frame, text="Comparison Results", padding="10")
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)

        self.comparison_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD,
                                                         width=100, height=25)
        self.comparison_text.pack(fill=tk.BOTH, expand=True)

    # ====== EARNINGS CALL METHODS ======

    def search_tickers(self):
        """Search for tickers using Massive API"""
        search_term = self.search_entry.get().strip()

        if not search_term:
            self.status_var.set("Enter a search term...")
            return

        self.status_var.set(f"Searching for '{search_term}'...")

        params = {
            "search": search_term,
            "limit": 50,
            "active": True
        }

        headers = {
            "Authorization": f"Bearer {MASSIVE_API_KEY}"
        }

        self.dropdown_values.clear()

        try:
            response = requests.get(MASSIVE_BASE_URL, params=params, headers=headers, timeout=10)

            if response.status_code == 200:
                data = response.json()

                for item in data.get("results", []):
                    display_text = f"{item['ticker']} — {item.get('name', 'Unknown')}"
                    self.dropdown_values.append(display_text)

                if self.dropdown_values:
                    self.ticker_combobox["values"] = self.dropdown_values
                    self.ticker_combobox.current(0)
                    self.status_var.set(f"Found {len(self.dropdown_values)} result(s)")
                else:
                    self.status_var.set("No tickers found")
            else:
                self.status_var.set(f"API Error: {response.status_code}")

        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

    def on_ticker_selected(self, event):
        """Handle ticker selection"""
        selected = self.ticker_combobox.get()
        ticker = selected.split(" — ")[0]

        self.selected_label.config(text=f"Selected: {selected}")
        self.current_ticker = ticker

    def analyze_earnings_call(self):
        """Main earnings call analysis function"""
        if not hasattr(self, 'current_ticker') or not self.current_ticker:
            messagebox.showwarning("No Ticker", "Please select a ticker first.")
            return

        # Show loading indicator
        self.show_loading(f"Analyzing earnings call for {self.current_ticker}...")
        self.disable_buttons_during_operation(True)

        # Run in thread to avoid GUI freezing
        thread = threading.Thread(target=self._analyze_earnings_call_thread)
        thread.daemon = True
        thread.start()

    def _analyze_earnings_call_thread(self):
        """Thread function for earnings call analysis"""
        try:
            ticker = self.current_ticker

            # Get fundamentals if requested
            fundamentals = None
            if self.include_fundamentals.get():
                self.root.after(0, lambda: self.loading_label.config(
                    text=f"Fetching fundamentals for {ticker}..."))
                fundamentals = get_stock_fundamentals(ticker)

            # Scrape earnings call
            self.root.after(0, lambda: self.loading_label.config(
                text=f"Scraping earnings call for {ticker}..."))
            call_text = self.scrape_earnings_call(ticker)

            if not call_text or "Error" in call_text:
                self.root.after(0, lambda: self.results_text.insert(
                    tk.END, f"Error: Could not retrieve earnings call for {ticker}\n"))
                self.root.after(0, self.hide_loading)
                self.root.after(0, lambda: self.disable_buttons_during_operation(False))
                return

            # Generate AI analysis
            self.root.after(0, lambda: self.loading_label.config(
                text=f"Generating AI analysis for {ticker}..."))
            self.root.after(0, lambda: self.results_text.insert(
                tk.END, f"Generating AI analysis for {ticker}...\n"))

            analysis = self.ai_explainer.explain_earnings_call(
                ticker=ticker,
                call_text=call_text,
                fundamentals=fundamentals
            )

            # Display results
            self.root.after(0, lambda: self.display_earnings_analysis(ticker, analysis))

            # Save to portfolio if requested
            if self.save_to_portfolio.get():
                self.root.after(0, lambda: self.add_earnings_to_portfolio(ticker, analysis))

        except Exception as e:
            self.root.after(0, lambda: self.results_text.insert(
                tk.END, f"Error during analysis: {str(e)}\n"))
        finally:
            # Always hide loading indicator and re-enable buttons
            self.root.after(0, self.hide_loading)
            self.root.after(0, lambda: self.disable_buttons_during_operation(False))
            self.root.after(0, lambda: self.status_var.set(f"Analysis complete for {ticker}"))

    def scrape_earnings_call(self, ticker):
        """Scrape earnings call from website"""
        if not self.driver:
            return "Selenium not available for web scraping."

        try:
            # Update loading message
            self.root.after(0, lambda: self.loading_label.config(
                text=f"Navigating to earnings call site..."))

            self.driver.get("https://earningscall.biz/")

            self.root.after(0, lambda: self.loading_label.config(
                text=f"Searching for {ticker}..."))

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "form-control"))
            )

            search_box = self.driver.find_element(By.CLASS_NAME, "form-control")
            search_box.clear()
            search_box.send_keys(ticker + Keys.RETURN)

            # Wait for results and select first company
            self.root.after(0, lambda: self.loading_label.config(
                text=f"Selecting company for {ticker}..."))

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "name-and-label"))
            )
            self.driver.find_element(By.CLASS_NAME, "name-and-label").click()

            # Select most recent call
            self.root.after(0, lambda: self.loading_label.config(
                text=f"Selecting most recent earnings call..."))

            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located(
                    (By.XPATH,
                     "/html/body/div/div[1]/div/main/section[2]/div/div[2]/div/div/div/table[1]/tbody/tr[1]/td[5]/a")
                )
            )
            self.driver.find_element(By.XPATH,
                                     "/html/body/div/div[1]/div/main/section[2]/div/div[2]/div/div/div/table[1]/tbody/tr[1]/td[5]/a").click()

            # Extract text
            self.root.after(0, lambda: self.loading_label.config(
                text=f"Extracting earnings call transcript..."))

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            page_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()

            # Extract between "share" and "about us"
            start_idx = page_text.find("share") + len("share")
            end_idx = page_text.find("about us\n", start_idx)

            if start_idx != -1 and end_idx != -1:
                return page_text[start_idx:end_idx]
            else:
                return page_text[:5000]  # Return first 5000 chars if pattern not found

        except Exception as e:
            return f"Error scraping earnings call: {str(e)}"

    def display_earnings_analysis(self, ticker, analysis):
        """Display earnings analysis in results"""
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, f"=== EARNINGS CALL ANALYSIS: {ticker} ===\n\n")
        self.results_text.insert(tk.END, f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        self.results_text.insert(tk.END, "=" * 60 + "\n\n")
        self.results_text.insert(tk.END, analysis)
        self.results_text.insert(tk.END, f"\n\n{'=' * 60}\nEnd of Analysis\n")

    # ====== PORTFOLIO METHODS ======

    def add_holding_to_portfolio(self):
        """Add a holding to the portfolio"""
        ticker = self.holding_ticker.get().strip().upper()
        shares_text = self.holding_shares.get().strip()

        if not ticker:
            messagebox.showwarning("Missing Ticker", "Please enter a ticker symbol.")
            return

        try:
            shares = float(shares_text)
        except ValueError:
            messagebox.showwarning("Invalid Shares", "Please enter a valid number for shares.")
            return

        portfolio_name = self.portfolio_name.get()

        self.status_var.set(f"Adding {ticker} to portfolio...")

        # Add to portfolio analyzer
        holding = self.portfolio_analyzer.add_holding(ticker, shares, portfolio_name)
        self.current_holdings.append(holding)

        # Update treeview
        self.update_holdings_tree()

        self.status_var.set(f"Added {ticker} to portfolio")

    def update_holdings_tree(self):
        """Update the holdings treeview"""
        # Clear tree
        for item in self.holdings_tree.get_children():
            self.holdings_tree.delete(item)

        # Add holdings
        for holding in self.current_holdings:
            value = holding.last_price * holding.shares if holding.last_price and holding.shares else 0

            # Check if we have earnings data
            has_earnings = "Yes" if hasattr(holding,
                                            'sentiment_score') and holding.sentiment_score is not None else "No"

            self.holdings_tree.insert("", tk.END, values=(
                holding.ticker,
                holding.shares or 0,
                f"${holding.last_price:.2f}" if holding.last_price else "N/A",
                f"${value:.2f}" if value else "N/A",
                holding.sector or "N/A",
                holding.beta if holding.beta else "N/A",
                has_earnings
            ))

    def analyze_portfolio(self):
        """Analyze the entire portfolio"""
        if not self.current_holdings:
            messagebox.showinfo("Empty Portfolio", "Add some holdings to analyze first.")
            return

        # Show loading indicator
        self.show_loading("Analyzing portfolio...")
        self.disable_buttons_during_operation(True)

        # Run in thread
        thread = threading.Thread(target=self._analyze_portfolio_thread)
        thread.daemon = True
        thread.start()

    def _analyze_portfolio_thread(self):
        """Thread function for portfolio analysis"""
        try:
            # Update loading message
            self.root.after(0, lambda: self.loading_label.config(
                text="Calculating portfolio metrics..."))

            # Get portfolio snapshot
            snapshot = self.portfolio_analyzer.analyze_portfolio()

            self.root.after(0, lambda: self.loading_label.config(
                text="Analyzing sector allocation..."))

            # Get sector allocation
            sector_allocation = self.portfolio_analyzer.get_sector_allocation()

            self.root.after(0, lambda: self.loading_label.config(
                text="Gathering earnings insights..."))

            # Get earnings insights
            earnings_insights = self.portfolio_analyzer.get_earnings_insights()

            self.root.after(0, lambda: self.loading_label.config(
                text="Generating AI analysis..."))

            # Generate AI analysis
            portfolio_data = {
                'total_value': snapshot.total_value or 0,
                'num_positions': snapshot.num_positions,
                'health_score': snapshot.health_score or 0,
                'sector_allocation': sector_allocation
            }

            # Get any earnings analyses we have
            earnings_analyses = []
            for holding in self.current_holdings:
                if hasattr(holding, 'earnings_analysis'):
                    earnings_analyses.append({
                        'ticker': holding.ticker,
                        'summary': holding.earnings_analysis[:200] if holding.earnings_analysis else "No analysis"
                    })

            analysis = self.ai_explainer.analyze_portfolio_with_earnings(
                portfolio_data=portfolio_data,
                earnings_analyses=earnings_analyses
            )

            # Display results
            self.root.after(0, lambda: self.display_portfolio_analysis(
                snapshot, sector_allocation, earnings_insights, analysis))

        except Exception as e:
            self.root.after(0, lambda: self.portfolio_text.insert(
                tk.END, f"Error during portfolio analysis: {str(e)}\n"))
        finally:
            # Always hide loading indicator
            self.root.after(0, self.hide_loading)
            self.root.after(0, lambda: self.disable_buttons_during_operation(False))
            self.root.after(0, lambda: self.status_var.set("Portfolio analysis complete"))

    def display_portfolio_analysis(self, snapshot, sector_allocation, earnings_insights, ai_analysis):
        """Display portfolio analysis results"""
        self.portfolio_text.delete(1.0, tk.END)

        # Basic metrics
        self.portfolio_text.insert(tk.END, "=== PORTFOLIO ANALYSIS ===\n\n")
        self.portfolio_text.insert(tk.END, f"Portfolio: {self.portfolio_name.get()}\n")
        self.portfolio_text.insert(tk.END, f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        self.portfolio_text.insert(tk.END, "=" * 60 + "\n\n")

        self.portfolio_text.insert(tk.END, "BASIC METRICS:\n")
        self.portfolio_text.insert(tk.END, f"• Total Value: ${snapshot.total_value:,.2f}\n")
        self.portfolio_text.insert(tk.END, f"• Number of Positions: {snapshot.num_positions}\n")
        self.portfolio_text.insert(tk.END, f"• Health Score: {snapshot.health_score}/100\n")
        self.portfolio_text.insert(tk.END, f"• Concentration Risk: {snapshot.concentration_risk:.1%}\n")

        if snapshot.avg_sentiment_score:
            self.portfolio_text.insert(tk.END, f"• Avg. Earnings Sentiment: {snapshot.avg_sentiment_score:.2f}\n")

        # Sector allocation
        self.portfolio_text.insert(tk.END, "\nSECTOR ALLOCATION:\n")
        for sector, weight in sector_allocation.items():
            self.portfolio_text.insert(tk.END, f"• {sector}: {weight:.1%}\n")

        # Earnings insights
        self.portfolio_text.insert(tk.END, "\nEARNINGS INSIGHTS:\n")
        if earnings_insights["holdings_with_recent_earnings"]:
            self.portfolio_text.insert(tk.END,
                                       f"• Holdings with earnings data: {len(earnings_insights['holdings_with_recent_earnings'])}/{snapshot.num_positions}\n")
        if earnings_insights["positive_outlooks"]:
            self.portfolio_text.insert(tk.END,
                                       f"• Positive outlooks: {', '.join(earnings_insights['positive_outlooks'][:3])}\n")
        if earnings_insights["risk_warnings"]:
            self.portfolio_text.insert(tk.END,
                                       f"• Risk warnings: {', '.join(earnings_insights['risk_warnings'][:3])}\n")

        # AI Analysis
        self.portfolio_text.insert(tk.END, "\n" + "=" * 60 + "\n")
        self.portfolio_text.insert(tk.END, "AI-POWERED ANALYSIS:\n")
        self.portfolio_text.insert(tk.END, "=" * 60 + "\n\n")
        self.portfolio_text.insert(tk.END, ai_analysis)

    def add_earnings_to_portfolio(self, ticker, analysis):
        """Add earnings analysis to a holding in the portfolio"""
        for holding in self.current_holdings:
            if holding.ticker == ticker:
                holding.earnings_analysis = analysis
                holding.earnings_analyzed = True
                holding.latest_earnings_call = datetime.now()
                break

    def compare_earnings_calls(self):
        """Compare multiple earnings calls"""
        tickers = [
            self.comp_ticker1.get().strip().upper(),
            self.comp_ticker2.get().strip().upper(),
            self.comp_ticker3.get().strip().upper()
        ]

        # Filter out empty tickers
        tickers = [t for t in tickers if t]

        if len(tickers) < 2:
            messagebox.showwarning("Not Enough Tickers", "Enter at least 2 tickers to compare.")
            return

        # Show loading indicator
        self.show_loading(f"Comparing earnings calls for {', '.join(tickers)}...")
        self.disable_buttons_during_operation(True)

        # Run in thread
        thread = threading.Thread(target=self._compare_earnings_thread, args=(tickers,))
        thread.daemon = True
        thread.start()

    def _compare_earnings_thread(self, tickers):
        """Thread function for earnings comparison"""
        try:
            analyses = []

            for i, ticker in enumerate(tickers):
                # Update loading message for each ticker
                self.root.after(0, lambda t=ticker, idx=i + 1: self.loading_label.config(
                    text=f"Analyzing {t} ({idx}/{len(tickers)})..."))

                # Scrape earnings call
                call_text = self.scrape_earnings_call(ticker)

                if call_text and not call_text.startswith("Error"):
                    # Simple analysis for comparison
                    fundamentals = get_stock_fundamentals(ticker)

                    analysis = {
                        'ticker': ticker,
                        'sentiment': 'Neutral',  # Simplified
                        'key_themes': 'Extracted from call',
                        'guidance': 'Based on management discussion'
                    }
                    analyses.append(analysis)

            # Update loading message
            self.root.after(0, lambda: self.loading_label.config(
                text="Generating comparative analysis..."))

            # Generate comparative analysis
            comparison = self.ai_explainer.compare_multiple_earnings(tickers, analyses)

            # Display results
            self.root.after(0, lambda: self.display_comparison(tickers, comparison))

        except Exception as e:
            self.root.after(0, lambda: self.comparison_text.insert(
                tk.END, f"Error during comparison: {str(e)}\n"))
        finally:
            # Always hide loading indicator
            self.root.after(0, self.hide_loading)
            self.root.after(0, lambda: self.disable_buttons_during_operation(False))
            self.root.after(0, lambda: self.status_var.set(
                f"Comparison complete for {len(tickers)} tickers"))

    def display_comparison(self, tickers, comparison):
        """Display comparison results"""
        self.comparison_text.delete(1.0, tk.END)
        self.comparison_text.insert(tk.END, f"=== EARNINGS CALL COMPARISON ===\n\n")
        self.comparison_text.insert(tk.END, f"Companies: {', '.join(tickers)}\n")
        self.comparison_text.insert(tk.END, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        self.comparison_text.insert(tk.END, "=" * 80 + "\n\n")
        self.comparison_text.insert(tk.END, comparison)
        self.comparison_text.insert(tk.END, f"\n\n{'=' * 80}\nEnd of Comparison\n")

    # ====== UTILITY METHODS ======

    def clear_results(self):
        """Clear earnings analysis results"""
        self.results_text.delete(1.0, tk.END)

    def clear_portfolio(self):
        """Clear the portfolio"""
        if messagebox.askyesno("Clear Portfolio", "Are you sure you want to clear the portfolio?"):
            self.current_holdings.clear()
            self.portfolio_analyzer = PortfolioAnalyzer()
            self.update_holdings_tree()
            self.portfolio_text.delete(1.0, tk.END)
            self.status_var.set("Portfolio cleared")

    def load_sample_portfolio(self):
        """Load a sample portfolio"""
        sample_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

        self.status_var.set(f"Loading sample portfolio with {len(sample_tickers)} holdings...")

        # Clear current portfolio
        self.current_holdings.clear()
        self.portfolio_analyzer = PortfolioAnalyzer()

        # Add each holding
        for ticker in sample_tickers:
            try:
                # Use a smaller number of shares to avoid huge portfolio values
                shares = 10  # Instead of 100

                # Add to portfolio analyzer
                holding = self.portfolio_analyzer.add_holding(ticker, shares, "Sample Portfolio")
                self.current_holdings.append(holding)

                # Add some mock earnings data for demonstration
                if ticker in ["AAPL", "MSFT"]:  # Add earnings data for some holdings
                    mock_summary = f"Mock earnings summary for {ticker}: Strong quarter with growth in key segments."
                    sentiment = 0.4 if ticker == "AAPL" else 0.3
                    self.portfolio_analyzer.add_earnings_call(ticker, "Mock call text", mock_summary, sentiment)

            except Exception as e:
                print(f"Error adding {ticker}: {e}")
                # Add holding with default values if API fails
                holding = EnhancedHolding(
                    ticker=ticker.upper(),
                    shares=10,
                    portfolio_name="Sample Portfolio",
                    last_price=100.0,  # Default price
                    sector="Technology",
                    beta=1.0
                )
                self.current_holdings.append(holding)

        # Update the treeview
        self.update_holdings_tree()

        # Show portfolio summary
        self.portfolio_text.delete(1.0, tk.END)
        self.portfolio_text.insert(tk.END, f"Sample portfolio loaded with {len(sample_tickers)} holdings.\n")
        self.portfolio_text.insert(tk.END, f"Holdings: {', '.join(sample_tickers)}\n")
        self.portfolio_text.insert(tk.END, "\nClick 'Analyze Portfolio' for detailed analysis.\n")

        self.status_var.set(f"Loaded sample portfolio with {len(sample_tickers)} holdings")

    def export_analysis(self):
        """Export current analysis to file"""
        # This would be implemented to save analysis to JSON or text file
        messagebox.showinfo("Export", "Export functionality would be implemented here")

    def on_closing(self):
        """Cleanup on window close"""
        # Re-enable buttons before closing
        self.disable_buttons_during_operation(False)

        if hasattr(self, 'driver') and self.driver:
            self.driver.quit()
        self.root.destroy()

    def show_loading(self, message="Processing..."):
        """Show loading indicator with message"""
        self.loading_label.config(text=message)
        self.loading_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        self.loading_progress.start(10)
        self.root.update()  # Force GUI update

    def hide_loading(self):
        """Hide loading indicator"""
        self.loading_progress.stop()
        self.loading_frame.pack_forget()
        self.root.update()


def disable_buttons_during_operation(self, disable=True):
    """Disable/enable action buttons during long operations"""
    state = "disabled" if disable else "normal"

    # Only disable buttons that actually exist
    buttons_to_check = []

    # Add buttons from different parts of the GUI
    if hasattr(self, 'search_button') and self.search_button:
        buttons_to_check.append(self.search_button)

    if hasattr(self, 'details_button') and self.details_button:
        buttons_to_check.append(self.details_button)

    if hasattr(self, 'analyze_button') and self.analyze_button:
        buttons_to_check.append(self.analyze_button)

    if hasattr(self, 'add_holding_button') and self.add_holding_button:
        buttons_to_check.append(self.add_holding_button)

    # Check all children for buttons (safer approach)
    for widget_name in ['search_frame', 'results_frame', 'button_frame',
                        'earnings_frame', 'portfolio_frame', 'comparison_frame']:
        if hasattr(self, widget_name):
            frame = getattr(self, widget_name)
            self._disable_buttons_in_frame(frame, state)

    # Also update the specific buttons we tried to use
    for button in buttons_to_check:
        if button and hasattr(button, 'winfo_exists') and button.winfo_exists():
            try:
                button.config(state=state)
            except:
                pass


def _disable_buttons_in_frame(self, frame, state):
    """Disable all buttons in a frame"""
    try:
        for child in frame.winfo_children():
            if isinstance(child, (tk.Button, ttk.Button)):
                child.config(state=state)
            # Also check children of children
            for grandchild in child.winfo_children():
                if isinstance(grandchild, (tk.Button, ttk.Button)):
                    grandchild.config(state=state)
    except:
        pass
def main():
    root = tk.Tk()
    app = EnhancedEarningsAnalyzer(root)

    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    root.mainloop()


if __name__ == "__main__":
    main()