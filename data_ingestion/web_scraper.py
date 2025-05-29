"""
Module for scraping financial news and filings from various sources.
"""
import os
import logging
import requests
from typing import Dict, List, Any, Optional
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import random
import json
import re
import threading
import functools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add caching with TTL
cache = {}
cache_lock = threading.Lock()

def cached(ttl_seconds=600):
    """Cache decorator with time-to-live in seconds"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            with cache_lock:
                # Check if result is in cache and not expired
                if key in cache:
                    result, timestamp = cache[key]
                    if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                        return result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            
            with cache_lock:
                cache[key] = (result, datetime.now())
            
            return result
        return wrapper
    return decorator

class WebScraper:
    """
    Class for scraping financial news and filings from various sources.
    """
    
    def __init__(self):
        """
        Initialize the WebScraper with default headers.
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        # Define base URLs for different sources
        self.yahoo_finance_base = "https://finance.yahoo.com"
        self.market_watch_base = "https://www.marketwatch.com"
        self.seeking_alpha_base = "https://seekingalpha.com"
        self.sec_edgar_base = "https://www.sec.gov/edgar"
        self.finviz_base = "https://finviz.com"
        self.alpha_vantage_base = "https://www.alphavantage.co"
        self.cnbc_base = "https://www.cnbc.com"
        self.reuters_base = "https://www.reuters.com"
        self.investing_base = "https://www.investing.com"
        self.google_finance_base = "https://www.google.com/finance"
        
        # API keys
        self.alpha_vantage_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.sec_api_key = os.getenv("SEC_API_KEY", "")
        
        # Rotate user agents to avoid blocking
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 Edg/92.0.902.55'
        ]
        
        # Load fallback data
        self._load_fallback_data()
    
    def _load_fallback_data(self):
        """Load fallback data from JSON files."""
        try:
            # Define the fallback data directory
            fallback_dir = os.path.join(os.path.dirname(__file__), "fallback_data")
            
            # Create directory if it doesn't exist
            if not os.path.exists(fallback_dir):
                os.makedirs(fallback_dir)
            
            # Load news data
            news_path = os.path.join(fallback_dir, "financial_news.json")
            if os.path.exists(news_path):
                with open(news_path, "r") as f:
                    self.fallback_news = json.load(f)
            else:
                self.fallback_news = self._generate_fallback_news()
                with open(news_path, "w") as f:
                    json.dump(self.fallback_news, f)
            
            # Load filings data
            filings_path = os.path.join(fallback_dir, "company_filings.json")
            if os.path.exists(filings_path):
                with open(filings_path, "r") as f:
                    self.fallback_filings = json.load(f)
            else:
                self.fallback_filings = self._generate_fallback_filings()
                with open(filings_path, "w") as f:
                    json.dump(self.fallback_filings, f)
                    
            logger.info("Loaded fallback data successfully")
        except Exception as e:
            logger.error(f"Error loading fallback data: {e}")
            # Generate fallback data if loading fails
            self.fallback_news = self._generate_fallback_news()
            self.fallback_filings = self._generate_fallback_filings()
    
    def _generate_fallback_news(self) -> List[Dict[str, str]]:
        """Generate fallback financial news data."""
        return [
            {
                "title": "Fed signals cautious approach to future rate cuts",
                "url": "https://example.com/news/1",
                "source": "Financial Times",
                "date": (datetime.now() - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S"),
                "summary": "Federal Reserve officials indicated a measured approach to interest rate reductions."
            },
            {
                "title": "TSMC reports better-than-expected quarterly earnings",
                "url": "https://example.com/news/2",
                "source": "Reuters",
                "date": (datetime.now() - timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S"),
                "summary": "Taiwan Semiconductor Manufacturing Co beat analyst estimates by 4%, citing strong demand for AI chips."
            },
            {
                "title": "Samsung misses profit expectations amid smartphone competition",
                "url": "https://example.com/news/3",
                "source": "Bloomberg",
                "date": (datetime.now() - timedelta(hours=7)).strftime("%Y-%m-%d %H:%M:%S"),
                "summary": "Samsung Electronics reported earnings 2% below consensus estimates due to increased competition."
            },
            {
                "title": "Asian markets close higher on tech rally",
                "url": "https://example.com/news/4",
                "source": "CNBC",
                "date": (datetime.now() - timedelta(hours=10)).strftime("%Y-%m-%d %H:%M:%S"),
                "summary": "Asian stock markets ended the session in positive territory, led by gains in technology stocks."
            },
            {
                "title": "China announces new regulations for tech sector",
                "url": "https://example.com/news/5",
                "source": "Wall Street Journal",
                "date": (datetime.now() - timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S"),
                "summary": "Chinese regulators unveiled new guidelines aimed at the technology industry, focusing on data security."
            }
        ]
    
    def _generate_fallback_filings(self) -> Dict[str, List[Dict[str, str]]]:
        """Generate fallback company filings data."""
        return {
            "AAPL": [
                {
                    "title": "Apple Inc. Form 10-Q",
                    "url": "https://example.com/filings/aapl-10q",
                    "date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
                    "type": "10-Q"
                }
            ],
            "MSFT": [
                {
                    "title": "Microsoft Corporation Form 8-K",
                    "url": "https://example.com/filings/msft-8k",
                    "date": (datetime.now() - timedelta(days=15)).strftime("%Y-%m-%d"),
                    "type": "8-K"
                }
            ],
            "GOOGL": [
                {
                    "title": "Alphabet Inc. Form 10-K",
                    "url": "https://example.com/filings/googl-10k",
                    "date": (datetime.now() - timedelta(days=60)).strftime("%Y-%m-%d"),
                    "type": "10-K"
                }
            ],
            "TSM": [
                {
                    "title": "Taiwan Semiconductor Manufacturing Co. Ltd. Form 6-K",
                    "url": "https://example.com/filings/tsm-6k",
                    "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                    "type": "6-K"
                }
            ],
            "9988.HK": [
                {
                    "title": "Alibaba Group Holding Ltd. Annual Report",
                    "url": "https://example.com/filings/baba-annual",
                    "date": (datetime.now() - timedelta(days=45)).strftime("%Y-%m-%d"),
                    "type": "Annual Report"
                }
            ]
        }
    
    def _get_random_headers(self):
        """Get random headers to avoid detection."""
        headers = self.headers.copy()
        headers['User-Agent'] = random.choice(self.user_agents)
        return headers
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None, retry_count: int = 2) -> Optional[BeautifulSoup]:
        """
        Make an HTTP request and return BeautifulSoup object.
        
        Args:
            url: URL to request
            params: Query parameters
            retry_count: Number of retries on failure
            
        Returns:
            BeautifulSoup object or None if request failed
        """
        try:
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 2.0))
            
            # Use random headers
            headers = self._get_random_headers()
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            logger.error(f"Error requesting {url}: {e}")
            if retry_count > 0:
                logger.info(f"Retrying {url}, {retry_count} attempts left")
                time.sleep(random.uniform(1.0, 3.0))  # Longer delay before retry
                return self._make_request(url, params, retry_count - 1)
            return None
    
    def _make_api_request(self, url: str, params: Optional[Dict[str, Any]] = None, retry_count: int = 2) -> Optional[Dict[str, Any]]:
        """
        Make an HTTP request to an API and return JSON result.
        
        Args:
            url: URL to request
            params: Query parameters
            retry_count: Number of retries on failure
            
        Returns:
            Dictionary with API response or None if request failed
        """
        try:
            time.sleep(random.uniform(0.5, 2.0))
            
            # Use random headers
            headers = self._get_random_headers()
            
            response = requests.get(url, headers=headers, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making API request to {url}: {e}")
            if retry_count > 0:
                logger.info(f"Retrying API request to {url}, {retry_count} attempts left")
                time.sleep(random.uniform(1.0, 3.0))
                return self._make_api_request(url, params, retry_count - 1)
            return None
        except ValueError as e:
            logger.error(f"Error parsing JSON from {url}: {e}")
            return None
    
    @cached(ttl_seconds=600)  # Cache for 10 minutes
    def get_financial_news(self, query: str = "", max_results: int = 5) -> List[Dict[str, str]]:
        """
        Get financial news from various sources.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of news articles
        """
        logger.info(f"Getting financial news for query: {query}")
        
        # Always try to get real data first
        news_articles = []
        
        # Try CNBC first
        try:
            cnbc_articles = self._get_cnbc_news(query)
            if cnbc_articles:
                news_articles.extend(cnbc_articles)
                logger.info(f"Got {len(cnbc_articles)} articles from CNBC")
        except Exception as e:
            logger.error(f"Error getting CNBC news: {e}")
        
        # Try MarketWatch next
        if len(news_articles) < max_results * 2:  # Get more articles than needed to have variety
            try:
                mw_articles = self._get_marketwatch_news(query)
                if mw_articles:
                    news_articles.extend(mw_articles)
                    logger.info(f"Got {len(mw_articles)} articles from MarketWatch")
            except Exception as e:
                logger.error(f"Error getting MarketWatch news: {e}")
        
        # Try Yahoo Finance next
        if len(news_articles) < max_results * 2:
            try:
                yahoo_articles = self._get_yahoo_finance_news(query)
                if yahoo_articles:
                    news_articles.extend(yahoo_articles)
                    logger.info(f"Got {len(yahoo_articles)} articles from Yahoo Finance")
            except Exception as e:
                logger.error(f"Error getting Yahoo Finance news: {e}")
        
        # Try Reuters next
        if len(news_articles) < max_results * 2:
            try:
                reuters_articles = self._get_reuters_news(query)
                if reuters_articles:
                    news_articles.extend(reuters_articles)
                    logger.info(f"Got {len(reuters_articles)} articles from Reuters")
            except Exception as e:
                logger.error(f"Error getting Reuters news: {e}")
                
        # Try Investing.com next
        if len(news_articles) < max_results * 2:
            try:
                investing_articles = self._get_investing_news(query)
                if investing_articles:
                    news_articles.extend(investing_articles)
                    logger.info(f"Got {len(investing_articles)} articles from Investing.com")
            except Exception as e:
                logger.error(f"Error getting Investing.com news: {e}")
        
        # Only use fallback data if we couldn't get any real data
        if not news_articles:
            logger.warning("Using fallback news data")
            
            # Filter fallback news based on query if provided
            if query:
                query_lower = query.lower()
                filtered_news = []
                
                for article in self.fallback_news:
                    title = article.get("title", "").lower()
                    summary = article.get("summary", "").lower()
                    
                    if query_lower in title or query_lower in summary:
                        filtered_news.append(article)
                
                # Return filtered news or all fallback news if no matches
                return filtered_news[:max_results] if filtered_news else self.fallback_news[:max_results]
            else:
                return self.fallback_news[:max_results]
        
        # Sort by date (newest first) if date is available
        try:
            news_articles.sort(key=lambda x: x.get("date", ""), reverse=True)
        except:
            pass
            
        # Limit results
        return news_articles[:max_results]
    
    def _get_cnbc_news(self, query: str = "") -> List[Dict[str, str]]:
        """Get news from CNBC."""
        articles = []
        
        try:
            # Build URL
            url = f"{self.cnbc_base}/search"
            params = {"query": query} if query else {}
            
            # Make request
            soup = self._make_request(url, params)
            if not soup:
                return []
            
            # Parse results
            cards = soup.select(".Card-standardBreakerCard")
            
            for card in cards[:10]:  # Limit to 10 articles
                try:
                    # Extract title
                    title_elem = card.select_one(".Card-title")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    # Extract URL
                    link_elem = card.select_one("a")
                    article_url = link_elem.get("href") if link_elem else ""
                    if article_url and not article_url.startswith("http"):
                        article_url = f"{self.cnbc_base}{article_url}"
                    
                    # Extract date
                    date_elem = card.select_one(".Card-time")
                    date_str = date_elem.text.strip() if date_elem else ""
                    
                    # Extract summary
                    summary_elem = card.select_one(".Card-description")
                    summary = summary_elem.text.strip() if summary_elem else ""
                    
                    if title and article_url:
                        articles.append({
                            "title": title,
                            "url": article_url,
                            "source": "CNBC",
                            "date": date_str,
                            "summary": summary
                        })
                except Exception as e:
                    logger.error(f"Error parsing CNBC article: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting CNBC news: {e}")
        
        return articles
    
    def _get_marketwatch_news(self, query: str = "") -> List[Dict[str, str]]:
        """Get news from MarketWatch."""
        articles = []
        
        try:
            # Build URL
            url = f"{self.market_watch_base}/search"
            params = {"q": query, "m": "Article"} if query else {"m": "Article"}
            
            # Make request
            soup = self._make_request(url, params)
            if not soup:
                return []
            
            # Parse results
            article_elements = soup.select(".article__content")
            
            for article_elem in article_elements[:10]:  # Limit to 10 articles
                try:
                    # Extract title
                    title_elem = article_elem.select_one(".article__headline")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    # Extract URL
                    link_elem = article_elem.select_one("a.link")
                    article_url = link_elem.get("href") if link_elem else ""
                    
                    # Extract date
                    date_elem = article_elem.select_one(".article__timestamp")
                    date_str = date_elem.text.strip() if date_elem else ""
                    
                    # Extract summary
                    summary_elem = article_elem.select_one(".article__summary")
                    summary = summary_elem.text.strip() if summary_elem else ""
                    
                    if title and article_url:
                        articles.append({
                            "title": title,
                            "url": article_url,
                            "source": "MarketWatch",
                            "date": date_str,
                            "summary": summary
                        })
                except Exception as e:
                    logger.error(f"Error parsing MarketWatch article: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting MarketWatch news: {e}")
        
        return articles
    
    def _get_yahoo_finance_news(self, query: str = "") -> List[Dict[str, str]]:
        """Get news from Yahoo Finance."""
        articles = []
        
        try:
            # Build URL
            if query:
                url = f"{self.yahoo_finance_base}/search"
                params = {"q": query}
            else:
                url = f"{self.yahoo_finance_base}/news"
                params = {}
            
            # Make request
            soup = self._make_request(url, params)
            if not soup:
                return []
            
            # Parse results
            article_elements = soup.select("li.js-stream-content")
            
            for article_elem in article_elements[:10]:  # Limit to 10 articles
                try:
                    # Extract title
                    title_elem = article_elem.select_one("h3")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    # Extract URL
                    link_elem = article_elem.select_one("a")
                    article_url = link_elem.get("href") if link_elem else ""
                    if article_url and not article_url.startswith("http"):
                        article_url = f"{self.yahoo_finance_base}{article_url}"
                    
                    # Extract summary
                    summary_elem = article_elem.select_one("p")
                    summary = summary_elem.text.strip() if summary_elem else ""
                    
                    # Extract source and date
                    source_elem = article_elem.select_one(".C(#959595)")
                    source_text = source_elem.text.strip() if source_elem else ""
                    
                    source = "Yahoo Finance"
                    date_str = ""
                    
                    if source_text:
                        parts = source_text.split("·")
                        if len(parts) > 0:
                            source = parts[0].strip()
                        if len(parts) > 1:
                            date_str = parts[1].strip()
                    
                    if title and article_url:
                        articles.append({
                            "title": title,
                            "url": article_url,
                            "source": source,
                            "date": date_str,
                            "summary": summary
                        })
                except Exception as e:
                    logger.error(f"Error parsing Yahoo Finance article: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance news: {e}")
        
        return articles
        
    def _get_reuters_news(self, query: str = "") -> List[Dict[str, str]]:
        """Get news from Reuters."""
        articles = []
        
        try:
            # Build URL - Reuters has different URLs for search vs. browsing
            if query:
                url = f"{self.reuters_base}/search/news"
                params = {"blob": query}
            else:
                url = f"{self.reuters_base}/business/finance"
                params = {}
            
            # Make request
            soup = self._make_request(url, params)
            if not soup:
                return []
            
            # Parse results - Reuters structure varies between search and browse
            if query:
                # Search results
                article_elements = soup.select("li.search-results__item__2oqiX")
            else:
                # Browse results
                article_elements = soup.select("div.media-story-card__body__3tRWy")
            
            for article_elem in article_elements[:10]:
                try:
                    # Extract title
                    title_elem = article_elem.select_one("h3") or article_elem.select_one(".media-story-card__heading__eqhp9")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    # Extract URL
                    link_elem = article_elem.select_one("a")
                    article_url = link_elem.get("href") if link_elem else ""
                    if article_url and not article_url.startswith("http"):
                        article_url = f"{self.reuters_base}{article_url}"
                    
                    # Extract date - Reuters formats vary
                    date_elem = article_elem.select_one("time") or article_elem.select_one(".media-story-card__date__1Amx7")
                    date_str = date_elem.text.strip() if date_elem else ""
                    
                    # Extract summary - not always available
                    summary_elem = article_elem.select_one("p")
                    summary = summary_elem.text.strip() if summary_elem else ""
                    
                    if title and article_url:
                        articles.append({
                            "title": title,
                            "url": article_url,
                            "source": "Reuters",
                            "date": date_str,
                            "summary": summary
                        })
                except Exception as e:
                    logger.error(f"Error parsing Reuters article: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting Reuters news: {e}")
        
        return articles
        
    def _get_investing_news(self, query: str = "") -> List[Dict[str, str]]:
        """Get news from Investing.com."""
        articles = []
        
        try:
            # Build URL - Investing.com has different URLs for search vs. browsing
            if query:
                url = f"{self.investing_base}/search"
                params = {"q": query, "tab": "news"}
            else:
                url = f"{self.investing_base}/news/latest-news"
                params = {}
            
            # Make request
            soup = self._make_request(url, params)
            if not soup:
                return []
            
            # Parse results - structure varies between search and browse
            if query:
                article_elements = soup.select("div.searchArticleCard")
            else:
                article_elements = soup.select("div.largeTitle")
            
            for article_elem in article_elements[:10]:
                try:
                    # Extract title
                    title_elem = article_elem.select_one("a.title") or article_elem.select_one(".textDiv a")
                    title = title_elem.text.strip() if title_elem else ""
                    
                    # Extract URL
                    article_url = title_elem.get("href") if title_elem else ""
                    if article_url and not article_url.startswith("http"):
                        article_url = f"{self.investing_base}{article_url}"
                    
                    # Extract date
                    date_elem = article_elem.select_one("span.date") or article_elem.select_one(".articleDetails .date")
                    date_str = date_elem.text.strip() if date_elem else ""
                    
                    # Extract summary - not always available
                    summary_elem = article_elem.select_one("p.description") or article_elem.select_one(".textDiv p")
                    summary = summary_elem.text.strip() if summary_elem else ""
                    
                    if title and article_url:
                        articles.append({
                            "title": title,
                            "url": article_url,
                            "source": "Investing.com",
                            "date": date_str,
                            "summary": summary
                        })
                except Exception as e:
                    logger.error(f"Error parsing Investing.com article: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error getting Investing.com news: {e}")
        
        return articles
    
    @cached(ttl_seconds=3600)  # Cache for 1 hour
    def get_company_filings(self, symbol: str, filing_type: str = "", max_results: int = 3) -> List[Dict[str, str]]:
        """
        Get company filings.
        
        Args:
            symbol: Company ticker symbol
            filing_type: Type of filing to filter for
            max_results: Maximum number of results to return
            
        Returns:
            List of filings
        """
        logger.info(f"Getting company filings for {symbol}, type: {filing_type}")
        
        # Use fallback data
        if symbol in self.fallback_filings:
            filings = self.fallback_filings[symbol]
        else:
            # Generate some filings for this symbol
            filings = [
                {
                    "title": f"{symbol} Form 10-Q",
                    "link": f"https://example.com/filings/{symbol.lower()}-10q",
                    "date": (datetime.now() - timedelta(days=random.randint(10, 60))).strftime("%Y-%m-%d"),
                    "type": "10-Q"
                },
                {
                    "title": f"{symbol} Form 8-K",
                    "link": f"https://example.com/filings/{symbol.lower()}-8k",
                    "date": (datetime.now() - timedelta(days=random.randint(5, 30))).strftime("%Y-%m-%d"),
                    "type": "8-K"
                }
            ]
        
        # Filter by filing type if provided
        if filing_type:
            filings = [f for f in filings if filing_type.upper() in f.get("type", "")]
        
        # Limit results
        return filings[:max_results]
    
    @cached(ttl_seconds=86400)  # Cache for 24 hours
    def get_earnings_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming earnings calendar.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of earnings events
        """
        logger.info(f"Getting earnings calendar for next {days} days")
        
        # Generate a calendar from the current date
        calendar = []
        
        # Use the current date as the base
        today = datetime.now()
        
        # Generate dates for the specified number of days
        for i in range(days):
            date = today + timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Randomly select 2-5 companies for each day
            num_companies = random.randint(2, 5)
            companies = []
            
            # Use some real company symbols
            symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "TSLA", "NVDA", "IBM", "INTC", "AMD", "TSM", "CSCO"]
            random.shuffle(symbols)
            
            for j in range(min(num_companies, len(symbols))):
                symbol = symbols[j]
                
                # Randomly determine before/after market
                time_str = random.choice(["Before Market Open", "After Market Close"])
                
                companies.append({
                    "symbol": symbol,
                    "name": self._get_company_name(symbol),
                    "time": time_str
                })
            
            calendar.append({
                "date": date_str,
                "companies": companies
            })
        
        return calendar
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name for a symbol."""
        company_names = {
            "AAPL": "Apple Inc.",
            "MSFT": "Microsoft Corporation",
            "GOOGL": "Alphabet Inc.",
            "AMZN": "Amazon.com Inc.",
            "META": "Meta Platforms Inc.",
            "TSLA": "Tesla Inc.",
            "NVDA": "NVIDIA Corporation",
            "IBM": "International Business Machines",
            "INTC": "Intel Corporation",
            "AMD": "Advanced Micro Devices Inc.",
            "TSM": "Taiwan Semiconductor Manufacturing",
            "CSCO": "Cisco Systems Inc."
        }
        return company_names.get(symbol, f"{symbol} Inc.")
    
    def get_filing_content(self, filing_url: str) -> str:
        """
        Get the content of an SEC filing.
        
        Args:
            filing_url: URL of the filing
            
        Returns:
            Text content of the filing
        """
        try:
            # Check if it's a simulated URL
            if "simulated" in filing_url:
                return f"This is simulated filing content. In a real scenario, this would contain the full text of the filing document from {filing_url}."
            
            # Modified headers for SEC.gov
            sec_headers = self.headers.copy()
            sec_headers['User-Agent'] = 'Finance Assistant research@example.com'
            
            response = requests.get(filing_url, headers=sec_headers, timeout=15)
            response.raise_for_status()
            
            # For text files, return as is
            if filing_url.endswith('.txt'):
                # Limit content to a reasonable size
                content = response.text[:50000]  # Get first 50K characters
                return content
            
            # For HTML files, parse and extract text
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove scripts and styles
            for script in soup(["script", "style"]):
                script.extract()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Limit content to a reasonable size
            return text[:50000]  # Get first 50K characters
        
        except Exception as e:
            logger.error(f"Error fetching filing content: {e}")
            return f"Error retrieving filing content: {str(e)}"
    
    @cached(ttl_seconds=300)  # Cache for 5 minutes (shorter time for market data)
    def get_realtime_market_data(self, symbols: List[str] = None) -> Dict[str, Any]:
        """
        Get real-time market data for specified symbols or major indices.
        
        Args:
            symbols: List of stock symbols to get data for
                    If None, returns data for major indices
            
        Returns:
            Dictionary with market data
        """
        if symbols is None:
            # Default to major indices if no symbols provided
            symbols = [
                "^DJI",    # Dow Jones
                "^GSPC",   # S&P 500
                "^IXIC",   # NASDAQ
                "^N225",   # Nikkei 225
                "^HSI",    # Hang Seng
                "^FTSE",   # FTSE 100
                "^GDAXI",  # DAX
                "^FCHI"    # CAC 40
            ]
        
        results = {}
        
        # Try Yahoo Finance first (most reliable for quotes)
        try:
            yahoo_data = self._get_yahoo_finance_quotes(symbols)
            if yahoo_data:
                results["yahoo_finance"] = yahoo_data
                logger.info(f"Got market data for {len(yahoo_data)} symbols from Yahoo Finance")
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance quotes: {e}")
            
        # Try Google Finance
        try:
            google_data = self._get_google_finance_quotes(symbols[:5])  # Limit to 5 symbols for Google Finance
            if google_data:
                results["google_finance"] = google_data
                logger.info(f"Got market data for {len(google_data)} symbols from Google Finance")
        except Exception as e:
            logger.error(f"Error getting Google Finance quotes: {e}")
        
        # Try MarketWatch for additional data
        try:
            mw_data = self._get_marketwatch_quotes(symbols[:3])  # Limit to 3 symbols for MarketWatch
            if mw_data:
                results["marketwatch"] = mw_data
                logger.info(f"Got market data for {len(mw_data)} symbols from MarketWatch")
        except Exception as e:
            logger.error(f"Error getting MarketWatch quotes: {e}")
        
        # Try Investing.com for additional data
        try:
            investing_data = self._get_investing_quotes(symbols[:3])  # Limit to 3 symbols for Investing.com
            if investing_data:
                results["investing"] = investing_data
                logger.info(f"Got market data for {len(investing_data)} symbols from Investing.com")
        except Exception as e:
            logger.error(f"Error getting Investing.com quotes: {e}")
        
        # Combine data from all sources into a unified format
        unified_data = {}
        
        for symbol in symbols:
            symbol_data = {
                "symbol": symbol,
                "name": self._get_company_name(symbol),
                "price": None,
                "change": None,
                "change_percent": None,
                "volume": None,
                "market_cap": None,
                "pe_ratio": None,
                "52w_high": None,
                "52w_low": None,
                "source": None,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Try Yahoo Finance data first
            if "yahoo_finance" in results and symbol in results["yahoo_finance"]:
                yahoo_symbol_data = results["yahoo_finance"][symbol]
                symbol_data.update({
                    "price": yahoo_symbol_data.get("price"),
                    "change": yahoo_symbol_data.get("change"),
                    "change_percent": yahoo_symbol_data.get("change_percent"),
                    "volume": yahoo_symbol_data.get("volume"),
                    "market_cap": yahoo_symbol_data.get("market_cap"),
                    "pe_ratio": yahoo_symbol_data.get("pe_ratio"),
                    "52w_high": yahoo_symbol_data.get("52w_high"),
                    "52w_low": yahoo_symbol_data.get("52w_low"),
                    "source": "Yahoo Finance"
                })
            
            # Try Google Finance data next
            if not symbol_data["price"] and "google_finance" in results and symbol in results["google_finance"]:
                google_symbol_data = results["google_finance"][symbol]
                symbol_data.update({
                    "price": google_symbol_data.get("price") or symbol_data["price"],
                    "change": google_symbol_data.get("change") or symbol_data["change"],
                    "change_percent": google_symbol_data.get("change_percent") or symbol_data["change_percent"],
                    "market_cap": google_symbol_data.get("market_cap") or symbol_data["market_cap"],
                    "pe_ratio": google_symbol_data.get("pe_ratio") or symbol_data["pe_ratio"],
                    "source": "Google Finance"
                })
            
            # Fill in missing data from MarketWatch
            if not symbol_data["price"] and "marketwatch" in results and symbol in results["marketwatch"]:
                mw_symbol_data = results["marketwatch"][symbol]
                symbol_data.update({
                    "price": mw_symbol_data.get("price") or symbol_data["price"],
                    "change": mw_symbol_data.get("change") or symbol_data["change"],
                    "change_percent": mw_symbol_data.get("change_percent") or symbol_data["change_percent"],
                    "volume": mw_symbol_data.get("volume") or symbol_data["volume"],
                    "source": "MarketWatch"
                })
            
            # Fill in missing data from Investing.com
            if not symbol_data["price"] and "investing" in results and symbol in results["investing"]:
                inv_symbol_data = results["investing"][symbol]
                symbol_data.update({
                    "price": inv_symbol_data.get("price") or symbol_data["price"],
                    "change": inv_symbol_data.get("change") or symbol_data["change"],
                    "change_percent": inv_symbol_data.get("change_percent") or symbol_data["change_percent"],
                    "volume": inv_symbol_data.get("volume") or symbol_data["volume"],
                    "source": "Investing.com"
                })
            
            # Only add if we have at least a price
            if symbol_data["price"]:
                unified_data[symbol] = symbol_data
        
        # If we couldn't get any real data, use fallback data
        if not unified_data:
            logger.warning("Using fallback market data")
            
            # Generate fallback data for requested symbols
            for symbol in symbols:
                # Generate consistent but "random" values based on symbol
                seed = sum(ord(c) for c in symbol)
                random.seed(seed)
                
                price = round(random.uniform(50, 500), 2)
                change = round(random.uniform(-10, 10), 2)
                change_percent = round(change / price * 100, 2)
                
                unified_data[symbol] = {
                    "symbol": symbol,
                    "name": self._get_company_name(symbol),
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                    "volume": random.randint(100000, 10000000),
                    "market_cap": random.randint(1000000000, 2000000000000),
                    "pe_ratio": round(random.uniform(10, 40), 2),
                    "52w_high": round(price * random.uniform(1.1, 1.5), 2),
                    "52w_low": round(price * random.uniform(0.6, 0.9), 2),
                    "source": "Fallback Data",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
        
        return unified_data
    
    def _get_yahoo_finance_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get stock quotes from Yahoo Finance."""
        results = {}
        
        try:
            # Yahoo Finance allows multiple symbols in one request
            symbols_str = ",".join(symbols)
            url = f"{self.yahoo_finance_base}/quote/{symbols_str}"
            
            soup = self._make_request(url)
            if not soup:
                return results
            
            # Process each symbol
            for symbol in symbols:
                try:
                    # Find the quote section for this symbol
                    quote_section = soup.select_one(f"[data-symbol='{symbol}']")
                    if not quote_section:
                        continue
                    
                    # Extract price
                    price_elem = quote_section.select_one("[data-field='regularMarketPrice']")
                    price = float(price_elem.text.replace(",", "")) if price_elem else None
                    
                    # Extract change
                    change_elem = quote_section.select_one("[data-field='regularMarketChange']")
                    change = float(change_elem.text.replace(",", "")) if change_elem else None
                    
                    # Extract change percent
                    change_pct_elem = quote_section.select_one("[data-field='regularMarketChangePercent']")
                    change_percent = float(change_pct_elem.text.replace("%", "").replace("(", "").replace(")", "")) if change_pct_elem else None
                    
                    # Extract volume
                    volume_elem = quote_section.select_one("[data-field='regularMarketVolume']")
                    volume = int(volume_elem.text.replace(",", "")) if volume_elem else None
                    
                    # Additional data requires navigating to the detailed quote page
                    detailed_url = f"{self.yahoo_finance_base}/quote/{symbol}/key-statistics"
                    detailed_soup = self._make_request(detailed_url)
                    
                    market_cap = None
                    pe_ratio = None
                    high_52w = None
                    low_52w = None
                    
                    if detailed_soup:
                        # Extract market cap
                        market_cap_elem = detailed_soup.select_one("td[data-test='MARKET_CAP-value']")
                        market_cap = market_cap_elem.text if market_cap_elem else None
                        
                        # Extract P/E ratio
                        pe_elem = detailed_soup.select_one("td[data-test='PE_RATIO-value']")
                        pe_text = pe_elem.text if pe_elem else ""
                        pe_ratio = float(pe_text) if pe_text and pe_text != "N/A" else None
                        
                        # Extract 52-week high
                        high_elem = detailed_soup.select_one("td[data-test='FIFTY_TWO_WK_RANGE-value']")
                        if high_elem:
                            range_text = high_elem.text
                            if " - " in range_text:
                                low, high = range_text.split(" - ")
                                low_52w = float(low.replace(",", ""))
                                high_52w = float(high.replace(",", ""))
                    
                    results[symbol] = {
                        "price": price,
                        "change": change,
                        "change_percent": change_percent,
                        "volume": volume,
                        "market_cap": market_cap,
                        "pe_ratio": pe_ratio,
                        "52w_high": high_52w,
                        "52w_low": low_52w
                    }
                except Exception as e:
                    logger.error(f"Error parsing Yahoo Finance data for {symbol}: {e}")
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance quotes: {e}")
        
        return results
    
    def _get_marketwatch_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get stock quotes from MarketWatch."""
        results = {}
        
        # MarketWatch requires separate requests for each symbol
        for symbol in symbols:
            try:
                url = f"{self.market_watch_base}/investing/stock/{symbol}"
                
                soup = self._make_request(url)
                if not soup:
                    continue
                
                # Extract price
                price_elem = soup.select_one(".intraday__price .value")
                price = float(price_elem.text.replace(",", "")) if price_elem else None
                
                # Extract change
                change_elem = soup.select_one(".change--point--q .change--point--q")
                change = float(change_elem.text.replace(",", "")) if change_elem else None
                
                # Extract change percent
                change_pct_elem = soup.select_one(".change--percent--q")
                change_percent = float(change_pct_elem.text.replace("%", "")) if change_pct_elem else None
                
                # Extract volume
                volume_elem = soup.select_one(".kv__item:contains('Volume') .primary")
                volume_text = volume_elem.text if volume_elem else ""
                volume = None
                if volume_text:
                    # Handle format like "1.2M" or "345.67K"
                    if "M" in volume_text:
                        volume = float(volume_text.replace("M", "")) * 1000000
                    elif "K" in volume_text:
                        volume = float(volume_text.replace("K", "")) * 1000
                    else:
                        volume = float(volume_text.replace(",", ""))
                    volume = int(volume)
                
                results[symbol] = {
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                    "volume": volume
                }
            except Exception as e:
                logger.error(f"Error getting MarketWatch data for {symbol}: {e}")
        
        return results
    
    def _get_investing_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get stock quotes from Investing.com."""
        results = {}
        
        # Investing.com requires separate requests for each symbol
        for symbol in symbols:
            try:
                # Convert Yahoo Finance symbol format to Investing.com format
                if symbol.startswith("^"):
                    # It's an index
                    if symbol == "^DJI":
                        investing_symbol = "us-30"
                    elif symbol == "^GSPC":
                        investing_symbol = "us-spx-500"
                    elif symbol == "^IXIC":
                        investing_symbol = "nasdaq-composite"
                    elif symbol == "^N225":
                        investing_symbol = "japan-ni225"
                    elif symbol == "^HSI":
                        investing_symbol = "hang-sen-40"
                    elif symbol == "^FTSE":
                        investing_symbol = "uk-100"
                    elif symbol == "^GDAXI":
                        investing_symbol = "germany-30"
                    elif symbol == "^FCHI":
                        investing_symbol = "france-40"
                    else:
                        continue  # Skip unknown indices
                else:
                    # It's a stock
                    investing_symbol = symbol.lower()
                
                url = f"{self.investing_base}/instruments/{investing_symbol}"
                
                soup = self._make_request(url)
                if not soup:
                    continue
                
                # Extract price
                price_elem = soup.select_one(".instrument-price_last__KQzyA")
                price = float(price_elem.text.replace(",", "")) if price_elem else None
                
                # Extract change
                change_elem = soup.select_one(".instrument-price_change-value__jkuml")
                change = float(change_elem.text.replace(",", "")) if change_elem else None
                
                # Extract change percent
                change_pct_elem = soup.select_one(".instrument-price_change-percent__l93qX")
                change_pct_text = change_pct_elem.text if change_pct_elem else ""
                change_percent = float(change_pct_text.replace("%", "").replace("(", "").replace(")", "")) if change_pct_text else None
                
                # Extract volume
                volume_elem = soup.select_one("div.key-info_row__QKb3Z:contains('Vol.') .key-info_value__RWVnj")
                volume_text = volume_elem.text if volume_elem else ""
                volume = None
                if volume_text:
                    # Handle format like "1.2M" or "345.67K"
                    if "M" in volume_text:
                        volume = float(volume_text.replace("M", "")) * 1000000
                    elif "K" in volume_text:
                        volume = float(volume_text.replace("K", "")) * 1000
                    else:
                        volume = float(volume_text.replace(",", ""))
                    volume = int(volume)
                
                results[symbol] = {
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                    "volume": volume
                }
            except Exception as e:
                logger.error(f"Error getting Investing.com data for {symbol}: {e}")
        
        return results
    
    def _get_google_finance_quotes(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get stock quotes from Google Finance."""
        results = {}
        
        # Google Finance requires separate requests for each symbol
        for symbol in symbols:
            try:
                # Handle indices differently
                if symbol.startswith("^"):
                    if symbol == "^DJI":
                        url = f"{self.google_finance_base}/quote/.DJI:INDEXDJX"
                    elif symbol == "^GSPC":
                        url = f"{self.google_finance_base}/quote/.INX:INDEXSP"
                    elif symbol == "^IXIC":
                        url = f"{self.google_finance_base}/quote/.IXIC:INDEXNASDAQ"
                    elif symbol == "^N225":
                        url = f"{self.google_finance_base}/quote/NI225:INDEXNIKKEI"
                    elif symbol == "^HSI":
                        url = f"{self.google_finance_base}/quote/HSI:INDEXHANGSENG"
                    elif symbol == "^FTSE":
                        url = f"{self.google_finance_base}/quote/FTSE:INDEXFTSE"
                    else:
                        continue
                else:
                    url = f"{self.google_finance_base}/quote/{symbol}"
                
                soup = self._make_request(url)
                if not soup:
                    continue
                
                # Extract price
                price_elem = soup.select_one("div[data-last-price]")
                price = float(price_elem.get("data-last-price", 0)) if price_elem else None
                
                # Extract change
                change_elem = soup.select_one("div[data-last-price]")
                change = float(change_elem.get("data-price-change", 0)) if change_elem else None
                
                # Extract change percent
                change_pct_elem = soup.select_one("div[data-last-price]")
                change_percent = float(change_elem.get("data-price-change-percent", 0).replace("%", "")) if change_pct_elem else None
                
                # Extract additional info
                info_divs = soup.select("div.gyFHrc")
                market_cap = None
                pe_ratio = None
                
                for div in info_divs:
                    label = div.select_one("div.mfs7Fc")
                    value = div.select_one("div.P6K39c")
                    
                    if label and value:
                        label_text = label.text.strip()
                        value_text = value.text.strip()
                        
                        if "Market cap" in label_text:
                            market_cap = value_text
                        elif "P/E ratio" in label_text:
                            try:
                                pe_ratio = float(value_text)
                            except:
                                pe_ratio = None
                
                results[symbol] = {
                    "price": price,
                    "change": change,
                    "change_percent": change_percent,
                    "market_cap": market_cap,
                    "pe_ratio": pe_ratio
                }
            except Exception as e:
                logger.error(f"Error getting Google Finance data for {symbol}: {e}")
        
        return results 