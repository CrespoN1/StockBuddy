# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
MASSIVE_API_KEY = os.getenv("MASSIVE_API_KEY", "zg6LoRvK7kW53hpf5B05ft78DE8z7TSQ")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-13795f0f8029452ea0be459ad6db1383")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "X5184RQAARQKZG8O")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", DEEPSEEK_API_KEY)

# URLs
MASSIVE_BASE_URL = "https://api.massive.com/v3/reference/tickers"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
EARNINGS_CALL_URL = "https://earningscall.biz/"

# Database
DATABASE_URL = "sqlite:///./portfolio_earnings.db"

# Application Settings
MAX_TOKENS = 2000
SCRAPE_TIMEOUT = 15
ANALYSIS_TEMPERATURE = 0.3