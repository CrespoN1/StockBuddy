from fastapi import APIRouter, Depends, HTTPException, Query, Request

from app.api.deps import get_current_user
from app.core.rate_limiter import SEARCH_LIMIT, limiter
from app.schemas.stock import (
    NewsArticle,
    OHLCVBar,
    StockForecast,
    StockFundamentals,
    StockInfo,
    StockQuote,
    StockSearchResult,
    TechnicalIndicators,
)
from app.services import forecast, market_data, news, search, stock_data, technical_analysis

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/search", response_model=list[StockSearchResult])
@limiter.limit(SEARCH_LIMIT)
async def search_stocks(
    request: Request,
    q: str = Query(..., min_length=1),
    limit: int = Query(20, ge=1, le=50),
    _user_id: str = Depends(get_current_user),
):
    return await search.search_tickers(q, limit=limit)


@router.get("/{ticker}", response_model=StockInfo)
async def get_stock_info(
    ticker: str,
    _user_id: str = Depends(get_current_user),
):
    info = await stock_data.get_stock_info(ticker)
    if info is None:
        raise HTTPException(404, f"Stock info not found for {ticker}")
    return info


@router.get("/{ticker}/quote", response_model=StockQuote)
async def get_stock_quote(
    ticker: str,
    _user_id: str = Depends(get_current_user),
):
    price = await market_data.get_latest_price(ticker)
    return StockQuote(ticker=ticker.upper(), price=price)


@router.get("/{ticker}/fundamentals", response_model=StockFundamentals)
async def get_stock_fundamentals(
    ticker: str,
    _user_id: str = Depends(get_current_user),
):
    data = await market_data.get_stock_fundamentals(ticker)
    return StockFundamentals(ticker=ticker.upper(), **data)


@router.get("/{ticker}/history", response_model=list[OHLCVBar])
async def get_stock_history(
    ticker: str,
    period: str = Query("1y", pattern=r"^(1mo|3mo|6mo|1y|2y|5y|max)$"),
    _user_id: str = Depends(get_current_user),
):
    return await stock_data.get_stock_history(ticker, period)


@router.get("/{ticker}/technicals", response_model=TechnicalIndicators)
async def get_technicals(
    ticker: str,
    _user_id: str = Depends(get_current_user),
):
    result = await technical_analysis.get_technical_indicators(ticker)
    if result is None:
        raise HTTPException(404, f"Could not compute technicals for {ticker}")
    return result


@router.get("/{ticker}/news", response_model=list[NewsArticle])
async def get_stock_news(
    ticker: str,
    limit: int = Query(10, ge=1, le=50),
    _user_id: str = Depends(get_current_user),
):
    """Get recent news articles with sentiment for a stock."""
    return await news.get_stock_news(ticker, limit=limit)


@router.get("/{ticker}/forecast", response_model=StockForecast)
async def get_stock_forecast(
    ticker: str,
    days: int = Query(30, ge=7, le=90),
    _user_id: str = Depends(get_current_user),
):
    """Get price forecast for a stock using predictive model."""
    result = await forecast.get_forecast(ticker, forecast_days=days)
    if "error" in result:
        raise HTTPException(400, result["error"])
    return StockForecast(**result)
