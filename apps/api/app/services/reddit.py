"""
Reddit post fetcher for finance subreddits.

Fetches recent Reddit posts mentioning a stock ticker from
popular finance subreddits using the public Reddit JSON API.
"""

import structlog
import httpx

logger = structlog.stdlib.get_logger(__name__)

FINANCE_SUBREDDITS = ["wallstreetbets", "stocks", "investing", "stockmarket"]
REDDIT_SEARCH_URL = "https://www.reddit.com/search.json"
USER_AGENT = "StockBuddy/1.0 (stock portfolio tracker)"


async def get_reddit_posts(ticker: str, limit: int = 5) -> list[dict]:
    """Fetch recent Reddit posts about a ticker from finance subreddits.

    Uses the public Reddit JSON API (no authentication required).
    Rate limit: ~10 requests/minute. Callers iterating over multiple
    tickers should add asyncio.sleep(0.5) between calls.

    Returns list of dicts matching the RedditPost schema.
    """
    subreddit_query = " OR ".join(f"subreddit:{s}" for s in FINANCE_SUBREDDITS)
    query = f"${ticker.upper()} ({subreddit_query})"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                REDDIT_SEARCH_URL,
                params={
                    "q": query,
                    "sort": "new",
                    "t": "week",
                    "limit": min(limit, 25),
                },
                headers={"User-Agent": USER_AGENT},
            )

            if resp.status_code == 429:
                logger.warning("Reddit rate limit hit for %s", ticker)
                return []

            if resp.status_code != 200:
                logger.warning(
                    "Reddit API returned status %d for %s", resp.status_code, ticker
                )
                return []

            data = resp.json()
            children = data.get("data", {}).get("children", [])
            posts: list[dict] = []

            for child in children:
                post = child.get("data", {})
                selftext = post.get("selftext", "")
                posts.append(
                    {
                        "title": post.get("title", ""),
                        "selftext_preview": (
                            selftext[:200] + ("..." if len(selftext) > 200 else "")
                        ),
                        "score": post.get("score", 0),
                        "subreddit": post.get("subreddit", ""),
                        "url": f"https://www.reddit.com{post.get('permalink', '')}",
                        "created_utc": post.get("created_utc", 0),
                        "num_comments": post.get("num_comments", 0),
                        "author": post.get("author", "[deleted]"),
                        "flair": post.get("link_flair_text") or "",
                        "ticker": ticker.upper(),
                    }
                )

            return posts

    except httpx.RequestError as exc:
        logger.warning("Failed to fetch Reddit posts for %s: %s", ticker, exc)
        return []
    except Exception as exc:
        logger.warning(
            "Unexpected error fetching Reddit posts for %s: %s", ticker, exc
        )
        return []
