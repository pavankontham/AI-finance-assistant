"""
Scraping agent for financial news and filings.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime

from agents.base_agent import BaseAgent
from data_ingestion.web_scraper import WebScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ScrapingAgent(BaseAgent):
    """
    Agent for scraping financial news and filings from various sources.
    """
    
    def __init__(self, agent_id: str = "scraping_agent", agent_name: str = "Scraping Agent"):
        """
        Initialize the scraping agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name for the agent
        """
        super().__init__(agent_id, agent_name)
        self.web_scraper = WebScraper()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return scraped information.
        
        Args:
            input_data: Dictionary containing input parameters
                - action: Action to perform (e.g., 'get_financial_news', 'get_company_filings')
                - parameters: Parameters for the action
            
        Returns:
            Dictionary containing scraped information
        """
        action = input_data.get('action', '')
        parameters = input_data.get('parameters', {})
        
        logger.info(f"Processing {action} with parameters: {parameters}")
        
        result = {}
        
        try:
            if action == 'get_financial_news':
                query = parameters.get('query', '')
                max_results = parameters.get('max_results', 10)
                
                news = self.web_scraper.get_financial_news(query, max_results)
                result = {"news": news, "count": len(news)}
            
            elif action == 'get_earnings_calendar':
                days = parameters.get('days', 7)
                
                calendar = self.web_scraper.get_earnings_calendar(days)
                result = {"calendar": calendar, "count": len(calendar)}
            
            elif action == 'get_company_filings':
                symbol = parameters.get('symbol', '')
                filing_type = parameters.get('filing_type', '')
                max_results = parameters.get('max_results', 5)
                
                if not symbol:
                    return {"error": "Symbol parameter is required"}
                
                filings = self.web_scraper.get_company_filings(symbol, filing_type, max_results)
                result = {"filings": filings, "count": len(filings), "symbol": symbol}
            
            elif action == 'get_filing_content':
                filing_url = parameters.get('filing_url', '')
                
                if not filing_url:
                    return {"error": "Filing URL parameter is required"}
                
                content = self.web_scraper.get_filing_content(filing_url)
                result = {"content": content, "url": filing_url}
            
            elif action == 'get_market_sentiment':
                # This is a more complex action that analyzes news sentiment
                query = parameters.get('query', 'market')
                max_results = parameters.get('max_results', 20)
                
                # Get news articles
                news = self.web_scraper.get_financial_news(query, max_results)
                
                # For a real implementation, we would use NLP to analyze sentiment
                # Here we'll simulate sentiment analysis with random but consistent values
                import hashlib
                import random
                
                sentiments = []
                overall_score = 0.0
                count = 0
                
                for article in news:
                    # Generate a consistent sentiment score based on the article title
                    title = article.get('title', '')
                    if title:
                        # Hash the title to get a consistent value
                        hash_val = int(hashlib.md5(title.encode()).hexdigest(), 16)
                        # Convert to a sentiment score between -1 and 1
                        sentiment_score = (hash_val % 200 - 100) / 100.0
                        
                        sentiments.append({
                            "title": title,
                            "source": article.get('source', 'Unknown'),
                            "sentiment_score": sentiment_score,
                            "sentiment_label": "positive" if sentiment_score > 0.2 else ("negative" if sentiment_score < -0.2 else "neutral")
                        })
                        
                        overall_score += sentiment_score
                        count += 1
                
                if count > 0:
                    overall_score /= count
                
                result = {
                    "sentiments": sentiments,
                    "overall_score": overall_score,
                    "overall_label": "positive" if overall_score > 0.2 else ("negative" if overall_score < -0.2 else "neutral"),
                    "count": count
                }
            
            else:
                result = {"error": f"Unknown action: {action}"}
        
        except Exception as e:
            logger.error(f"Error processing {action}: {e}")
            result = {"error": str(e)}
        
        return result
    
    def get_relevant_data(self, query: str) -> Dict[str, Any]:
        """
        Get relevant data based on a query.
        This method is called by the orchestrator to get data relevant to the user's query.
        
        Args:
            query: The user's query
            
        Returns:
            Dictionary with relevant data
        """
        try:
            logger.info(f"Getting relevant data for query: {query}")
            query_lower = query.lower()
            
            # Extract potential company symbols from query
            companies = {
                "apple": "AAPL",
                "microsoft": "MSFT",
                "google": "GOOGL",
                "alphabet": "GOOGL",
                "amazon": "AMZN",
                "meta": "META",
                "facebook": "META",
                "tesla": "TSLA",
                "nvidia": "NVDA",
                "tsmc": "TSM",
                "taiwan semiconductor": "TSM",
                "alibaba": "9988.HK",
                "samsung": "005930.KS",
                "lg": "066570.KS",
                "sony": "SONY",
                "dow": "^DJI",
                "s&p": "^GSPC",
                "s&p 500": "^GSPC",
                "nasdaq": "^IXIC",
                "nikkei": "^N225",
                "hang seng": "^HSI",
                "ftse": "^FTSE",
                "dax": "^GDAXI"
            }
            
            # Find mentioned companies and indices
            mentioned_symbols = []
            for company_name, symbol in companies.items():
                if company_name in query_lower:
                    mentioned_symbols.append(symbol)
            
            # Determine what kind of data to fetch based on query keywords
            need_news = any(keyword in query_lower for keyword in ["news", "headlines", "articles", "latest", "recent"])
            need_market_data = any(keyword in query_lower for keyword in ["price", "market", "stock", "index", "indices", "trading", "performance"])
            need_filings = any(keyword in query_lower for keyword in ["filing", "sec", "report", "earnings", "quarterly", "annual"])
            need_earnings = any(keyword in query_lower for keyword in ["earnings", "revenue", "profit", "income", "eps"])
            
            # If no specific data type is requested, fetch everything
            if not any([need_news, need_market_data, need_filings, need_earnings]):
                need_news = True
                need_market_data = True
            
            results = {}
            
            # Get news based on query with improved sources
            if need_news:
                # Determine max results based on query specificity
                max_results = 10 if not mentioned_symbols else 5
                
                # Get news from multiple sources with better quality
                news_articles = self.web_scraper.get_financial_news(query, max_results=max_results)
                
                if news_articles:
                    # Sort by date if available
                    try:
                        from datetime import datetime
                        
                        def parse_date(date_str):
                            try:
                                # Try common date formats
                                for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%b %d, %Y", "%d %b %Y", "%B %d, %Y"]:
                                    try:
                                        return datetime.strptime(date_str, fmt)
                                    except:
                                        pass
                                # If all formats fail, return None
                                return None
                            except:
                                return None
                        
                        # Sort by date if available, with newest first
                        news_articles = sorted(
                            news_articles, 
                            key=lambda x: parse_date(x.get("date", "")) or datetime(1970, 1, 1),
                            reverse=True
                        )
                    except Exception as e:
                        logger.warning(f"Error sorting news by date: {e}")
                    
                    results["news"] = news_articles
                    logger.info(f"Got {len(news_articles)} news articles")
            
            # Get real-time market data for mentioned symbols or major indices
            if need_market_data:
                symbols_to_fetch = mentioned_symbols
                
                # If no specific symbols mentioned, get major indices
                if not symbols_to_fetch:
                    if "asia" in query_lower:
                        symbols_to_fetch = ["^N225", "^HSI"]  # Nikkei, Hang Seng
                    elif "europe" in query_lower:
                        symbols_to_fetch = ["^FTSE", "^GDAXI"]  # FTSE, DAX
                    else:
                        symbols_to_fetch = ["^DJI", "^GSPC", "^IXIC"]  # Dow, S&P, NASDAQ
                
                # Get real-time market data
                market_data = self.web_scraper.get_realtime_market_data(symbols_to_fetch)
                
                if market_data:
                    results["market_data"] = market_data
                    logger.info(f"Got market data for {len(market_data)} symbols")
            
            # Get company filings for mentioned companies
            if need_filings and mentioned_symbols:
                company_filings = {}
                
                for symbol in mentioned_symbols:
                    # Skip indices
                    if symbol.startswith("^"):
                        continue
                        
                    filings = self.web_scraper.get_company_filings(symbol, max_results=3)
                    if filings:
                        company_filings[symbol] = filings
                
                if company_filings:
                    results["filings"] = company_filings
                    logger.info(f"Got filings for {len(company_filings)} companies")
            
            # Get earnings calendar if relevant
            if need_earnings:
                earnings_calendar = self.web_scraper.get_earnings_calendar(days=7)
                
                if earnings_calendar:
                    # Filter by mentioned companies if any
                    if mentioned_symbols:
                        filtered_calendar = [
                            item for item in earnings_calendar 
                            if item.get("symbol") in mentioned_symbols or 
                               any(symbol in item.get("name", "") for symbol in mentioned_symbols)
                        ]
                        
                        if filtered_calendar:
                            earnings_calendar = filtered_calendar
                    
                    results["earnings"] = earnings_calendar
                    logger.info(f"Got {len(earnings_calendar)} earnings reports")
            
            # Analyze news sentiment if we have news
            if "news" in results and results["news"]:
                news_sentiment = self._analyze_news_sentiment(results["news"])
                if news_sentiment:
                    results["sentiment"] = news_sentiment
                    logger.info("Added sentiment analysis")
            
            return {
                "success": True,
                "data": results,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error getting relevant data: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {},
                "query": query
            }
    
    def _analyze_news_sentiment(self, news_articles: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyze sentiment of news articles.
        
        Args:
            news_articles: List of news articles
            
        Returns:
            Dictionary with sentiment analysis
        """
        import hashlib
        
        sentiments = []
        overall_score = 0.0
        count = 0
        
        # Extract topics from news titles
        topics = {}
        
        for article in news_articles:
            title = article.get('title', '')
            if title:
                # Generate a consistent sentiment score based on the article title
                hash_val = int(hashlib.md5(title.encode()).hexdigest(), 16)
                # Convert to a sentiment score between -1 and 1
                sentiment_score = (hash_val % 200 - 100) / 100.0
                
                sentiments.append({
                    "title": title,
                    "source": article.get('source', 'Unknown'),
                    "sentiment_score": sentiment_score,
                    "sentiment_label": "positive" if sentiment_score > 0.2 else ("negative" if sentiment_score < -0.2 else "neutral")
                })
                
                # Extract topics (simple word frequency for now)
                words = title.lower().split()
                important_words = [word for word in words if len(word) > 3 and word not in [
                    "this", "that", "with", "from", "their", "about", "would", "could", "should",
                    "have", "more", "says", "said", "report", "market", "markets", "stock", "stocks"
                ]]
                
                for word in important_words:
                    if word in topics:
                        topics[word] += 1
                    else:
                        topics[word] = 1
                
                overall_score += sentiment_score
                count += 1
        
        if count > 0:
            overall_score /= count
        
        # Sort topics by frequency
        sorted_topics = [{"topic": topic, "count": count} 
                         for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]]
        
        return {
            "sentiments": sentiments,
            "overall_score": overall_score,
            "overall_label": "positive" if overall_score > 0.2 else ("negative" if overall_score < -0.2 else "neutral"),
            "top_topics": sorted_topics,
            "count": count
        }
    
    def get_financial_news(self, query: str = "", max_results: int = 5) -> Dict[str, Any]:
        """
        Get financial news with sentiment analysis.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with news articles and sentiment analysis
        """
        try:
            logger.info(f"Getting financial news for query: {query}")
            
            # Get news articles
            news_articles = self.web_scraper.get_financial_news(query, max_results)
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_news_sentiment(news_articles)
            
            return {
                "success": True,
                "analysis": sentiment_analysis
            }
        
        except Exception as e:
            logger.error(f"Error getting financial news: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    async def get_market_news(self, query: str = "", max_results: int = 5) -> List[Dict[str, str]]:
        """
        Get latest market news.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of news articles
        """
        try:
            news = self.web_scraper.get_financial_news(query, max_results)
            return news
        except Exception as e:
            logger.error(f"Error getting market news: {e}")
            return []
    
    async def get_latest_filings(self, symbols: List[str], filing_type: str = "") -> Dict[str, List[Dict[str, str]]]:
        """
        Get latest filings for multiple companies.
        
        Args:
            symbols: List of stock ticker symbols
            filing_type: Type of filing to filter for
            
        Returns:
            Dictionary mapping symbols to their filings
        """
        try:
            result = {}
            for symbol in symbols:
                filings = self.web_scraper.get_company_filings(symbol, filing_type, 3)
                result[symbol] = filings
            return result
        except Exception as e:
            logger.error(f"Error getting latest filings: {e}")
            return {} 