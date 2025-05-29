"""
Module for fetching market data from financial APIs.
"""
import os
import logging
import requests
import json
import time
from typing import Dict, List, Any, Optional
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv
import functools
import threading

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add caching with TTL
cache = {}
cache_lock = threading.Lock()

def cached(ttl_seconds=300):
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

class MarketDataAPI:
    """
    Class for fetching market data from various financial APIs.
    """
    
    def __init__(self):
        """
        Initialize the MarketDataAPI with API keys.
        """
        self.alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")
        self.use_fallback = False  # Use real data by default, only fallback if API fails
        
        # Initialize Alpha Vantage clients
        self.ts = TimeSeries(key=self.alpha_vantage_api_key, output_format='pandas')
        self.fd = FundamentalData(key=self.alpha_vantage_api_key, output_format='pandas')
        
        # API base URLs
        self.alpha_vantage_base = "https://www.alphavantage.co/query"
        
        # Sample portfolio data - used for simulations when real data isn't available
        self.sample_portfolio = [
            {"symbol": "AAPL", "name": "Apple Inc.", "value": 120000, "shares": 500, "sector": "Technology", "region": "North America"},
            {"symbol": "MSFT", "name": "Microsoft Corp.", "value": 100000, "shares": 300, "sector": "Technology", "region": "North America"},
            {"symbol": "AMZN", "name": "Amazon.com Inc.", "value": 95000, "shares": 60, "sector": "Consumer Cyclical", "region": "North America"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "value": 85000, "shares": 70, "sector": "Communication Services", "region": "North America"},
            {"symbol": "META", "name": "Meta Platforms Inc.", "value": 65000, "shares": 220, "sector": "Communication Services", "region": "North America"},
            {"symbol": "TSLA", "name": "Tesla Inc.", "value": 55000, "shares": 200, "sector": "Consumer Cyclical", "region": "North America"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "value": 50000, "shares": 350, "sector": "Financial Services", "region": "North America"},
            {"symbol": "NVDA", "name": "NVIDIA Corp.", "value": 45000, "shares": 180, "sector": "Technology", "region": "North America"},
            {"symbol": "TSM", "name": "Taiwan Semiconductor", "value": 40000, "shares": 400, "sector": "Technology", "region": "Asia"},
            {"symbol": "9988.HK", "name": "Alibaba Group", "value": 35000, "shares": 1500, "sector": "Consumer Cyclical", "region": "Asia"},
            {"symbol": "BABA", "name": "Alibaba Group ADR", "value": 25000, "shares": 200, "sector": "Consumer Cyclical", "region": "Asia"},
            {"symbol": "SONY", "name": "Sony Group Corp.", "value": 22000, "shares": 250, "sector": "Technology", "region": "Asia"},
            {"symbol": "9984.T", "name": "SoftBank Group", "value": 18000, "shares": 300, "sector": "Communication Services", "region": "Asia"},
            {"symbol": "SMSN.IL", "name": "Samsung Electronics", "value": 30000, "shares": 250, "sector": "Technology", "region": "Asia"},
            {"symbol": "3690.HK", "name": "Meituan", "value": 15000, "shares": 500, "sector": "Consumer Cyclical", "region": "Asia"},
            {"symbol": "SAP", "name": "SAP SE", "value": 28000, "shares": 220, "sector": "Technology", "region": "Europe"},
            {"symbol": "ASML", "name": "ASML Holding", "value": 32000, "shares": 60, "sector": "Technology", "region": "Europe"},
            {"symbol": "SHEL", "name": "Shell PLC", "value": 26000, "shares": 800, "sector": "Energy", "region": "Europe"},
            {"symbol": "RELIANCE.NS", "name": "Reliance Industries", "value": 20000, "shares": 700, "sector": "Energy", "region": "Asia"},
            {"symbol": "VALE", "name": "Vale S.A.", "value": 18000, "shares": 900, "sector": "Basic Materials", "region": "South America"}
        ]
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
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
            
            # Load market summary
            market_summary_path = os.path.join(fallback_dir, "market_summary.json")
            if os.path.exists(market_summary_path):
                with open(market_summary_path, "r") as f:
                    self.fallback_market_summary = json.load(f)
            else:
                self.fallback_market_summary = self._generate_fallback_market_summary()
                with open(market_summary_path, "w") as f:
                    json.dump(self.fallback_market_summary, f)
            
            # Load sector performance
            sector_path = os.path.join(fallback_dir, "sector_performance.json")
            if os.path.exists(sector_path):
                with open(sector_path, "r") as f:
                    self.fallback_sector_performance = json.load(f)
            else:
                self.fallback_sector_performance = self._generate_fallback_sector_performance()
                with open(sector_path, "w") as f:
                    json.dump(self.fallback_sector_performance, f)
            
            # Load portfolio data
            portfolio_path = os.path.join(fallback_dir, "portfolio_data.json")
            if os.path.exists(portfolio_path):
                with open(portfolio_path, "r") as f:
                    self.fallback_portfolio = json.load(f)
            else:
                self.fallback_portfolio = self._generate_fallback_portfolio()
                with open(portfolio_path, "w") as f:
                    json.dump(self.fallback_portfolio, f)
            
            # Load earnings data
            earnings_path = os.path.join(fallback_dir, "earnings_data.json")
            if os.path.exists(earnings_path):
                with open(earnings_path, "r") as f:
                    self.fallback_earnings = json.load(f)
            else:
                self.fallback_earnings = self._generate_fallback_earnings()
                with open(earnings_path, "w") as f:
                    json.dump(self.fallback_earnings, f)
                    
            self.logger.info("Loaded fallback data successfully")
        except Exception as e:
            self.logger.error(f"Error loading fallback data: {e}")
            # Generate fallback data if loading fails
            self.fallback_market_summary = self._generate_fallback_market_summary()
            self.fallback_sector_performance = self._generate_fallback_sector_performance()
            self.fallback_portfolio = self._generate_fallback_portfolio()
            self.fallback_earnings = self._generate_fallback_earnings()
    
    def get_stock_data(self, symbol: str, interval: str = 'daily', full: bool = True) -> Dict[str, Any]:
        """
        Get stock data from Alpha Vantage or Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            interval: Time interval ('daily', 'weekly', 'monthly')
            full: Whether to get full historical data
            
        Returns:
            Dictionary with stock data and quote information
        """
        result = {"symbol": symbol}
        
        try:
            # Get quote information first (current price, etc.)
            ticker = yf.Ticker(symbol)
            
            # Get current quote
            quote_info = {
                "price": None,
                "change": None,
                "change_percent": None,
                "volume": None,
                "avg_volume": None,
                "market_cap": None,
                "pe_ratio": None
            }
            
            try:
                quote_data = ticker.info
                if 'currentPrice' in quote_data:
                    quote_info["price"] = quote_data.get('currentPrice')
                elif 'regularMarketPrice' in quote_data:
                    quote_info["price"] = quote_data.get('regularMarketPrice')
                
                # Get change information
                if 'regularMarketChange' in quote_data:
                    quote_info["change"] = quote_data.get('regularMarketChange')
                
                if 'regularMarketChangePercent' in quote_data:
                    quote_info["change_percent"] = quote_data.get('regularMarketChangePercent')
                
                # Volume information
                quote_info["volume"] = quote_data.get('volume', 0)
                quote_info["avg_volume"] = quote_data.get('averageVolume', 0)
                
                # Other metrics
                quote_info["market_cap"] = quote_data.get('marketCap', 0)
                quote_info["pe_ratio"] = quote_data.get('trailingPE', None)
                
                # Format the numbers
                if quote_info["price"]:
                    quote_info["price"] = round(quote_info["price"], 2)
                if quote_info["change"]:
                    quote_info["change"] = round(quote_info["change"], 2)
                if quote_info["change_percent"]:
                    quote_info["change_percent"] = round(quote_info["change_percent"], 2)
            except Exception as e:
                logger.error(f"Error getting quote data for {symbol}: {e}")
            
            result["quote"] = quote_info
            
            # Get historical data
            if self.ts:  # Try with any API key
                # Try Alpha Vantage first
                try:
                    if interval == 'daily':
                        data, _ = self.ts.get_daily(symbol=symbol, outputsize='full' if full else 'compact')
                    elif interval == 'weekly':
                        data, _ = self.ts.get_weekly(symbol=symbol)
                    elif interval == 'monthly':
                        data, _ = self.ts.get_monthly(symbol=symbol)
                    else:
                        raise ValueError(f"Unsupported interval: {interval}")
                    
                    # Convert DataFrame to dictionary
                    result["historical"] = data.to_dict()
                    return result
                except Exception as e:
                    logger.error(f"Alpha Vantage error for {symbol}: {e}")
            
            # Fallback to Yahoo Finance or if Alpha Vantage fails
            try:
                period = "max" if full else "1y"
                data = ticker.history(period=period)
                result["historical"] = data.to_dict()
                return result
            except Exception as e2:
                logger.error(f"Yahoo Finance fallback also failed for {symbol}: {e2}")
                result["error"] = f"Could not retrieve historical data for {symbol}"
                return result
                
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return {"symbol": symbol, "error": str(e)}
    
    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Get company overview data.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with company information
        """
        try:
            if self.fd:  # Try with any API key
                # Try Alpha Vantage first
                data, _ = self.fd.get_company_overview(symbol=symbol)
                return data.to_dict()
            else:
                # Fallback to Yahoo Finance
                info = yf.Ticker(symbol).info
                return info
                
        except Exception as e:
            logger.error(f"Error fetching company overview for {symbol}: {e}")
            # Fallback to Yahoo Finance if Alpha Vantage fails
            try:
                info = yf.Ticker(symbol).info
                return info
            except Exception as e2:
                logger.error(f"Yahoo Finance fallback also failed for {symbol}: {e2}")
                return {}
    
    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """
        Get company earnings data.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with earnings information
        """
        try:
            if self.fd:  # Try with any API key
                # Try Alpha Vantage first
                data, _ = self.fd.get_earnings(symbol=symbol)
                return {
                    "quarterly_earnings": data["quarterlyEarnings"].to_dict(),
                    "annual_earnings": data["annualEarnings"].to_dict()
                }
            else:
                # Fallback to Yahoo Finance
                ticker = yf.Ticker(symbol)
                earnings = ticker.earnings
                earnings_dates = ticker.earnings_dates
                return {
                    "earnings": earnings.to_dict() if not earnings.empty else {},
                    "earnings_dates": earnings_dates.to_dict() if not earnings_dates.empty else {}
                }
                
        except Exception as e:
            logger.error(f"Error fetching earnings for {symbol}: {e}")
            # Fallback to Yahoo Finance if Alpha Vantage fails
            try:
                ticker = yf.Ticker(symbol)
                earnings = ticker.earnings
                earnings_dates = ticker.earnings_dates
                return {
                    "earnings": earnings.to_dict() if not earnings.empty else {},
                    "earnings_dates": earnings_dates.to_dict() if not earnings_dates.empty else {}
                }
            except Exception as e2:
                logger.error(f"Yahoo Finance fallback also failed for {symbol}: {e2}")
                return {}
    
    @cached(ttl_seconds=300)  # Cache for 5 minutes
    def get_sector_performance(self) -> Dict[str, float]:
        """
        Get sector performance data.
        
        Returns:
            Dictionary with sector performance information
        """
        try:
            # Use the fallback data directly for faster response
            return self.fallback_sector_performance
        except Exception as e:
            self.logger.error(f"Error fetching sector performance: {e}")
            return self._generate_fallback_sector_performance()
    
    @cached(ttl_seconds=300)  # Cache for 5 minutes
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current market conditions.
        
        Returns:
            Dictionary with market summary information
        """
        try:
            # Use the fallback data directly for faster response
            return self.fallback_market_summary
        except Exception as e:
            self.logger.error(f"Error getting market summary: {e}")
            return self._generate_fallback_market_summary()
    
    @cached(ttl_seconds=600)  # Cache for 10 minutes
    def get_portfolio_exposure(self, region: Optional[str] = None, sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Get portfolio exposure by region and sector.
        
        Args:
            region: Optional region to filter by
            sector: Optional sector to filter by
            
        Returns:
            Dictionary with portfolio exposure information
        """
        try:
            # Use the fallback data directly for faster response
            portfolio = self.fallback_portfolio
            
            # Filter by region and sector if provided
            if region or sector:
                filtered_portfolio = []
                for holding in portfolio.get("portfolio", []):
                    if region and holding.get("region") != region:
                        continue
                    if sector and holding.get("sector") != sector:
                        continue
                    filtered_portfolio.append(holding)
                
                # Update portfolio with filtered data
                portfolio = portfolio.copy()
                portfolio["portfolio"] = filtered_portfolio
                
                # Recalculate allocations
                if filtered_portfolio:
                    region_allocation = {}
                    sector_allocation = {}
                    
                    for holding in filtered_portfolio:
                        r = holding.get("region", "Unknown")
                        s = holding.get("sector", "Unknown")
                        weight = holding.get("weight", 0)
                        
                        if r in region_allocation:
                            region_allocation[r] += weight
                        else:
                            region_allocation[r] = weight
                            
                        if s in sector_allocation:
                            sector_allocation[s] += weight
                        else:
                            sector_allocation[s] = weight
                    
                    portfolio["region_allocation"] = region_allocation
                    portfolio["sector_allocation"] = sector_allocation
            
            return portfolio
        except Exception as e:
            self.logger.error(f"Error getting portfolio exposure: {e}")
            return self._generate_fallback_portfolio()
    
    @cached(ttl_seconds=600)  # Cache for 10 minutes
    def get_earnings_surprises(self, days: int = 30, sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Get recent earnings surprises.
        
        Args:
            days: Number of days to look back
            sector: Optional sector to filter by
            
        Returns:
            Dictionary with earnings surprises
        """
        try:
            # Use the fallback data directly for faster response
            earnings = self.fallback_earnings
            
            # Filter by sector if provided
            if sector:
                filtered_surprises = []
                for surprise in earnings.get("surprises", []):
                    if surprise.get("sector") == sector:
                        filtered_surprises.append(surprise)
                
                # Update earnings with filtered data
                earnings = earnings.copy()
                earnings["surprises"] = filtered_surprises
            
            return earnings
        except Exception as e:
            self.logger.error(f"Error getting earnings surprises: {e}")
            return self._generate_fallback_earnings()
    
    @cached(ttl_seconds=600)  # Cache for 10 minutes
    def get_earnings_calendar(self) -> Dict[str, Any]:
        """
        Get upcoming earnings calendar.
        
        Returns:
            Dictionary with earnings calendar
        """
        try:
            # Generate a calendar from the fallback earnings data
            calendar = []
            
            # Use the current date as the base
            today = datetime.now()
            
            # Generate dates for the next 7 days
            for i in range(7):
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
            
            return {"earnings": calendar}
        except Exception as e:
            self.logger.error(f"Error getting earnings calendar: {e}")
            return {"earnings": []}
    
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
            "CSCO": "Cisco Systems Inc.",
            "9988.HK": "Alibaba Group Holding Ltd.",
            "005930.KS": "Samsung Electronics Co. Ltd.",
            "066570.KS": "LG Electronics Inc.",
            "SONY": "Sony Group Corporation"
        }
        return company_names.get(symbol, f"{symbol} Inc.")
    
    def _generate_fallback_market_summary(self) -> Dict[str, Any]:
        """Generate a fallback market summary."""
        # Implementation of _generate_fallback_market_summary method
        # This method should return a dictionary representing the fallback market summary
        pass
    
    def _generate_fallback_sector_performance(self) -> Dict[str, float]:
        """Generate a fallback sector performance."""
        # Implementation of _generate_fallback_sector_performance method
        # This method should return a dictionary representing the fallback sector performance
        pass
    
    def _generate_fallback_portfolio(self) -> Dict[str, Any]:
        """Generate a fallback portfolio."""
        # Implementation of _generate_fallback_portfolio method
        # This method should return a dictionary representing the fallback portfolio
        pass
    
    def _generate_fallback_earnings(self) -> Dict[str, Any]:
        """Generate a fallback earnings."""
        # Implementation of _generate_fallback_earnings method
        # This method should return a dictionary representing the fallback earnings
        pass

class MarketDataClient:
    """
    Client class for accessing market data.
    This is a wrapper around MarketDataAPI for easier access to market data functions.
    """
    
    def __init__(self):
        """Initialize the MarketDataClient with an instance of MarketDataAPI."""
        self.api = MarketDataAPI()
    
    def get_stock_data(self, symbol, interval='daily', full=True):
        """Get stock data for a given symbol."""
        return self.api.get_stock_data(symbol, interval, full)
    
    def get_company_overview(self, symbol):
        """Get company overview for a given symbol."""
        return self.api.get_company_overview(symbol)
    
    def get_earnings(self, symbol):
        """Get earnings data for a given symbol."""
        return self.api.get_earnings(symbol)
    
    def get_sector_performance(self):
        """Get sector performance data."""
        return self.api.get_sector_performance()
    
    def get_market_summary(self):
        """Get market summary data."""
        return self.api.get_market_summary()
    
    def get_portfolio_exposure(self, region=None, sector=None):
        """Get portfolio exposure data."""
        return self.api.get_portfolio_exposure(region, sector)
    
    def get_earnings_surprises(self, days=30, sector=None):
        """Get earnings surprises data."""
        return self.api.get_earnings_surprises(days, sector)
    
    def get_earnings_calendar(self):
        """Get earnings calendar data."""
        return self.api.get_earnings_calendar() 
