"""
Market data API client for financial data.
"""
import os
import logging
import json
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketDataAPI:
    """
    API client for fetching market data from financial APIs.
    """
    
    def __init__(self):
        """Initialize the market data API client."""
        self.api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
    
    def get_stock_data(self, symbol: str, interval: str = "daily", full: bool = False) -> Dict[str, Any]:
        """
        Get stock data for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            interval: Data interval (daily, weekly, monthly)
            full: Whether to return full output
            
        Returns:
            Dictionary with stock data
        """
        logger.info(f"Getting {interval} stock data for {symbol}")
        
        try:
            # In a real implementation, this would make an API call
            # For this demo, we'll return simulated data
            
            # Generate a consistent price based on the symbol
            price_base = sum(ord(c) for c in symbol) % 1000
            price = price_base + random.uniform(-10, 10)
            
            # Generate a consistent change based on the symbol
            change_seed = sum(ord(c) * (i+1) for i, c in enumerate(symbol)) % 100
            change = (change_seed - 50) / 10
            
            # Calculate change percent
            change_percent = (change / price) * 100
            
            # Generate volume
            volume = int(random.uniform(1000000, 10000000))
            
            # Generate historical data if full output is requested
            historical_data = None
            if full:
                historical_data = []
                base_price = price
                for i in range(30):
                    date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                    daily_change = random.uniform(-5, 5)
                    daily_price = base_price + daily_change
                    daily_volume = int(random.uniform(800000, 1200000))
                    
                    historical_data.append({
                        "date": date,
                        "open": daily_price - random.uniform(0, 2),
                        "high": daily_price + random.uniform(0, 3),
                        "low": daily_price - random.uniform(0, 3),
                        "close": daily_price,
                        "volume": daily_volume
                    })
                    
                    base_price = daily_price
            
            # Create response
            response = {
                "symbol": symbol,
                "quote": {
                    "price": round(price, 2),
                    "change": round(change, 2),
                    "change_percent": round(change_percent, 2),
                    "volume": volume,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            if historical_data:
                response["historical"] = historical_data
            
            return response
            
        except Exception as e:
            logger.error(f"Error getting stock data for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_company_overview(self, symbol: str) -> Dict[str, Any]:
        """
        Get company overview data.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with company overview data
        """
        logger.info(f"Getting company overview for {symbol}")
        
        try:
            # In a real implementation, this would make an API call
            # For this demo, we'll return simulated data
            
            # Map of company symbols to data
            company_data = {
                "AAPL": {
                    "name": "Apple Inc.",
                    "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide.",
                    "exchange": "NASDAQ",
                    "currency": "USD",
                    "country": "USA",
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                    "employees": 154000
                },
                "MSFT": {
                    "name": "Microsoft Corporation",
                    "description": "Microsoft Corporation develops, licenses, and supports software, services, devices, and solutions worldwide.",
                    "exchange": "NASDAQ",
                    "currency": "USD",
                    "country": "USA",
                    "sector": "Technology",
                    "industry": "Software—Infrastructure",
                    "employees": 181000
                },
                "GOOGL": {
                    "name": "Alphabet Inc.",
                    "description": "Alphabet Inc. provides various products and platforms in the United States, Europe, the Middle East, Africa, the Asia-Pacific, Canada, and Latin America.",
                    "exchange": "NASDAQ",
                    "currency": "USD",
                    "country": "USA",
                    "sector": "Communication Services",
                    "industry": "Internet Content & Information",
                    "employees": 156500
                },
                "TSM": {
                    "name": "Taiwan Semiconductor Manufacturing Company Limited",
                    "description": "Taiwan Semiconductor Manufacturing Company Limited manufactures and sells integrated circuits and semiconductors.",
                    "exchange": "NYSE",
                    "currency": "USD",
                    "country": "Taiwan",
                    "sector": "Technology",
                    "industry": "Semiconductors",
                    "employees": 56800
                }
            }
            
            # Return company data if available, otherwise return generic data
            if symbol in company_data:
                return company_data[symbol]
            else:
                return {
                    "name": f"{symbol} Inc.",
                    "description": f"Company with ticker symbol {symbol}.",
                    "exchange": "NYSE",
                    "currency": "USD",
                    "country": "USA",
                    "sector": "Unknown",
                    "industry": "Unknown",
                    "employees": 10000
                }
            
        except Exception as e:
            logger.error(f"Error getting company overview for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_earnings(self, symbol: str) -> Dict[str, Any]:
        """
        Get earnings data for a company.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with earnings data
        """
        logger.info(f"Getting earnings data for {symbol}")
        
        try:
            # In a real implementation, this would make an API call
            # For this demo, we'll return simulated data
            
            # Generate quarterly earnings data
            quarterly_earnings = []
            for i in range(4):
                quarter_date = (datetime.now() - timedelta(days=i*90)).strftime("%Y-%m-%d")
                
                # Generate consistent EPS values based on symbol
                expected_eps = (sum(ord(c) for c in symbol) % 100) / 10
                actual_eps = expected_eps * (1 + (random.uniform(-0.2, 0.2)))
                surprise_percent = ((actual_eps - expected_eps) / expected_eps) * 100
                
                quarterly_earnings.append({
                    "date": quarter_date,
                    "quarter": f"Q{(4-i) % 4 + 1}",
                    "expected_eps": round(expected_eps, 2),
                    "actual_eps": round(actual_eps, 2),
                    "surprise": round(actual_eps - expected_eps, 2),
                    "surprise_percent": round(surprise_percent, 2)
                })
            
            return {
                "symbol": symbol,
                "quarterly_earnings": quarterly_earnings
            }
            
        except Exception as e:
            logger.error(f"Error getting earnings data for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_sector_performance(self) -> Dict[str, float]:
        """
        Get sector performance data.
        
        Returns:
            Dictionary mapping sector names to performance percentages
        """
        logger.info("Getting sector performance")
        
        try:
            # In a real implementation, this would make an API call
            # For this demo, we'll return simulated data
            
            sectors = {
                "Technology": random.uniform(-2, 5),
                "Healthcare": random.uniform(-2, 3),
                "Financial Services": random.uniform(-2, 2),
                "Consumer Cyclical": random.uniform(-3, 3),
                "Communication Services": random.uniform(-2, 4),
                "Industrials": random.uniform(-2, 2),
                "Consumer Defensive": random.uniform(-1, 1),
                "Energy": random.uniform(-4, 4),
                "Basic Materials": random.uniform(-3, 3),
                "Real Estate": random.uniform(-2, 2),
                "Utilities": random.uniform(-1, 1)
            }
            
            # Round values to 2 decimal places
            return {k: round(v, 2) for k, v in sectors.items()}
            
        except Exception as e:
            logger.error(f"Error getting sector performance: {e}")
            return {"error": str(e)}
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current market conditions.
        
        Returns:
            Dictionary with market summary information
        """
        logger.info("Getting market summary")
        
        try:
            # In a real implementation, this would make an API call
            # For this demo, we'll return simulated data
            
            # Generate index data
            indices = []
            
            # Dow Jones
            dow_price = 34000 + random.uniform(-500, 500)
            dow_change = random.uniform(-200, 200)
            indices.append({
                "symbol": "^DJI",
                "name": "Dow Jones Industrial Average",
                "price": round(dow_price, 2),
                "change": round(dow_change, 2),
                "change_percent": round((dow_change / dow_price) * 100, 2)
            })
            
            # S&P 500
            sp_price = 4500 + random.uniform(-100, 100)
            sp_change = random.uniform(-50, 50)
            indices.append({
                "symbol": "^GSPC",
                "name": "S&P 500",
                "price": round(sp_price, 2),
                "change": round(sp_change, 2),
                "change_percent": round((sp_change / sp_price) * 100, 2)
            })
            
            # NASDAQ
            nasdaq_price = 14000 + random.uniform(-300, 300)
            nasdaq_change = random.uniform(-100, 100)
            indices.append({
                "symbol": "^IXIC",
                "name": "NASDAQ Composite",
                "price": round(nasdaq_price, 2),
                "change": round(nasdaq_change, 2),
                "change_percent": round((nasdaq_change / nasdaq_price) * 100, 2)
            })
            
            # Nikkei 225
            nikkei_price = 28000 + random.uniform(-500, 500)
            nikkei_change = random.uniform(-200, 200)
            indices.append({
                "symbol": "^N225",
                "name": "Nikkei 225",
                "price": round(nikkei_price, 2),
                "change": round(nikkei_change, 2),
                "change_percent": round((nikkei_change / nikkei_price) * 100, 2)
            })
            
            # Hang Seng
            hs_price = 24000 + random.uniform(-500, 500)
            hs_change = random.uniform(-200, 200)
            indices.append({
                "symbol": "^HSI",
                "name": "Hang Seng Index",
                "price": round(hs_price, 2),
                "change": round(hs_change, 2),
                "change_percent": round((hs_change / hs_price) * 100, 2)
            })
            
            # Get sector performance
            sectors = self.get_sector_performance()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "indices": indices,
                "sectors": sectors
            }
            
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {"error": str(e)}
    
    def get_portfolio_exposure(self, region: Optional[str] = None, sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Get portfolio exposure by region and sector.
        
        Args:
            region: Optional region to filter by
            sector: Optional sector to filter by
            
        Returns:
            Dictionary with portfolio exposure information
        """
        logger.info(f"Getting portfolio exposure for region={region}, sector={sector}")
        
        try:
            # In a real implementation, this would fetch actual portfolio data
            # For this demo, we'll return simulated data
            
            # Define portfolio holdings
            portfolio = [
                {"symbol": "AAPL", "name": "Apple Inc.", "value": 120000, "shares": 500, "sector": "Technology", "region": "North America"},
                {"symbol": "MSFT", "name": "Microsoft Corp.", "value": 100000, "shares": 300, "sector": "Technology", "region": "North America"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "value": 90000, "shares": 40, "sector": "Communication Services", "region": "North America"},
                {"symbol": "AMZN", "name": "Amazon.com Inc.", "value": 85000, "shares": 25, "sector": "Consumer Cyclical", "region": "North America"},
                {"symbol": "TSM", "name": "Taiwan Semiconductor", "value": 40000, "shares": 400, "sector": "Technology", "region": "Asia"},
                {"symbol": "9988.HK", "name": "Alibaba Group", "value": 35000, "shares": 1500, "sector": "Consumer Cyclical", "region": "Asia"},
                {"symbol": "005930.KS", "name": "Samsung Electronics", "value": 30000, "shares": 500, "sector": "Technology", "region": "Asia"},
                {"symbol": "SONY", "name": "Sony Group Corp.", "value": 22000, "shares": 250, "sector": "Technology", "region": "Asia"},
                {"symbol": "ASML", "name": "ASML Holding", "value": 45000, "shares": 70, "sector": "Technology", "region": "Europe"},
                {"symbol": "SAP", "name": "SAP SE", "value": 28000, "shares": 200, "sector": "Technology", "region": "Europe"},
                {"symbol": "SHOP", "name": "Shopify Inc.", "value": 18000, "shares": 150, "sector": "Technology", "region": "North America"},
                {"symbol": "BABA", "name": "Alibaba Group ADR", "value": 15000, "shares": 150, "sector": "Consumer Cyclical", "region": "Asia"},
                {"symbol": "V", "name": "Visa Inc.", "value": 32000, "shares": 150, "sector": "Financial Services", "region": "North America"},
                {"symbol": "JPM", "name": "JPMorgan Chase", "value": 30000, "shares": 200, "sector": "Financial Services", "region": "North America"},
                {"symbol": "HSBC", "name": "HSBC Holdings", "value": 20000, "shares": 400, "sector": "Financial Services", "region": "Europe"}
            ]
            
            # Apply filters if provided
            filtered_portfolio = portfolio
            
            if region:
                filtered_portfolio = [h for h in filtered_portfolio if h["region"] == region]
            
            if sector:
                filtered_portfolio = [h for h in filtered_portfolio if h["sector"] == sector]
            
            # Calculate total value
            total_value = sum(h["value"] for h in portfolio)
            filtered_value = sum(h["value"] for h in filtered_portfolio)
            
            # Calculate allocation percentages
            for holding in filtered_portfolio:
                holding["weight"] = round((holding["value"] / total_value) * 100, 2)
            
            # Calculate region allocation
            region_allocation = {}
            for holding in portfolio:
                r = holding["region"]
                if r in region_allocation:
                    region_allocation[r] += holding["value"]
                else:
                    region_allocation[r] = holding["value"]
            
            # Convert to percentages
            region_allocation = {r: round((v / total_value) * 100, 2) for r, v in region_allocation.items()}
            
            # Calculate sector allocation
            sector_allocation = {}
            for holding in portfolio:
                s = holding["sector"]
                if s in sector_allocation:
                    sector_allocation[s] += holding["value"]
                else:
                    sector_allocation[s] = holding["value"]
            
            # Convert to percentages
            sector_allocation = {s: round((v / total_value) * 100, 2) for s, v in sector_allocation.items()}
            
            return {
                "portfolio": filtered_portfolio,
                "total_value": total_value,
                "filtered_value": filtered_value,
                "filtered_percentage": round((filtered_value / total_value) * 100, 2),
                "region_allocation": region_allocation,
                "sector_allocation": sector_allocation,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting portfolio exposure: {e}")
            return {"error": str(e)}
    
    def get_earnings_surprises(self, days: int = 30, sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Get recent earnings surprises.
        
        Args:
            days: Number of days to look back
            sector: Optional sector to filter by
            
        Returns:
            Dictionary with earnings surprises
        """
        logger.info(f"Getting earnings surprises for days={days}, sector={sector}")
        
        try:
            # In a real implementation, this would fetch actual earnings data
            # For this demo, we'll return simulated data
            
            # Define earnings surprises
            surprises = [
                {"symbol": "AAPL", "name": "Apple Inc.", "expected_eps": 1.45, "actual_eps": 1.52, "surprise_percent": 4.83, "date": "2023-04-28", "sector": "Technology"},
                {"symbol": "MSFT", "name": "Microsoft Corp.", "expected_eps": 2.23, "actual_eps": 2.35, "surprise_percent": 5.38, "date": "2023-04-25", "sector": "Technology"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "expected_eps": 1.34, "actual_eps": 1.44, "surprise_percent": 7.46, "date": "2023-04-25", "sector": "Communication Services"},
                {"symbol": "META", "name": "Meta Platforms Inc.", "expected_eps": 2.56, "actual_eps": 2.20, "surprise_percent": -14.06, "date": "2023-04-26", "sector": "Communication Services"},
                {"symbol": "AMZN", "name": "Amazon.com Inc.", "expected_eps": 0.21, "actual_eps": 0.31, "surprise_percent": 47.62, "date": "2023-04-27", "sector": "Consumer Cyclical"},
                {"symbol": "NFLX", "name": "Netflix Inc.", "expected_eps": 3.10, "actual_eps": 3.73, "surprise_percent": 20.32, "date": "2023-04-18", "sector": "Communication Services"},
                {"symbol": "TSLA", "name": "Tesla Inc.", "expected_eps": 0.85, "actual_eps": 0.73, "surprise_percent": -14.12, "date": "2023-04-19", "sector": "Consumer Cyclical"},
                {"symbol": "TSM", "name": "Taiwan Semiconductor", "expected_eps": 1.07, "actual_eps": 1.12, "surprise_percent": 4.67, "date": "2023-04-20", "sector": "Technology"},
                {"symbol": "INTC", "name": "Intel Corporation", "expected_eps": 0.13, "actual_eps": 0.10, "surprise_percent": -23.08, "date": "2023-04-27", "sector": "Technology"},
                {"symbol": "NVDA", "name": "NVIDIA Corporation", "expected_eps": 0.92, "actual_eps": 1.09, "surprise_percent": 18.48, "date": "2023-05-24", "sector": "Technology"},
                {"symbol": "AMD", "name": "Advanced Micro Devices", "expected_eps": 0.56, "actual_eps": 0.60, "surprise_percent": 7.14, "date": "2023-05-02", "sector": "Technology"},
                {"symbol": "SONY", "name": "Sony Group Corp.", "expected_eps": 0.58, "actual_eps": 0.62, "surprise_percent": 6.90, "date": "2023-05-10", "sector": "Technology"},
                {"symbol": "BABA", "name": "Alibaba Group", "expected_eps": 1.15, "actual_eps": 1.40, "surprise_percent": 21.74, "date": "2023-05-18", "sector": "Consumer Cyclical"},
                {"symbol": "005930.KS", "name": "Samsung Electronics", "expected_eps": 1.10, "actual_eps": 1.08, "surprise_percent": -1.82, "date": "2023-04-26", "sector": "Technology"}
            ]
            
            # Apply filters if provided
            filtered_surprises = surprises
            
            # Filter by sector if provided
            if sector:
                filtered_surprises = [s for s in filtered_surprises if s["sector"] == sector]
            
            # Filter by date range
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            filtered_surprises = [s for s in filtered_surprises if s["date"] >= cutoff_date]
            
            # Sort by date (most recent first)
            filtered_surprises = sorted(filtered_surprises, key=lambda x: x["date"], reverse=True)
            
            return {
                "surprises": filtered_surprises,
                "count": len(filtered_surprises),
                "days": days,
                "sector": sector,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting earnings surprises: {e}")
            return {"error": str(e)}
    
    def get_earnings_calendar(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get upcoming earnings calendar.
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            List of upcoming earnings reports
        """
        logger.info(f"Getting earnings calendar for next {days} days")
        
        try:
            # In a real implementation, this would fetch actual calendar data
            # For this demo, we'll return simulated data
            
            # Define earnings calendar
            calendar = [
                {"symbol": "AAPL", "name": "Apple Inc.", "report_date": "2023-07-25", "time": "AMC", "estimate_eps": 1.19, "sector": "Technology"},
                {"symbol": "MSFT", "name": "Microsoft Corp.", "report_date": "2023-07-25", "time": "AMC", "estimate_eps": 2.55, "sector": "Technology"},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "report_date": "2023-07-25", "time": "AMC", "estimate_eps": 1.34, "sector": "Communication Services"},
                {"symbol": "META", "name": "Meta Platforms Inc.", "report_date": "2023-07-26", "time": "AMC", "estimate_eps": 2.91, "sector": "Communication Services"},
                {"symbol": "AMZN", "name": "Amazon.com Inc.", "report_date": "2023-07-27", "time": "AMC", "estimate_eps": 0.35, "sector": "Consumer Cyclical"},
                {"symbol": "INTC", "name": "Intel Corporation", "report_date": "2023-07-27", "time": "AMC", "estimate_eps": 0.20, "sector": "Technology"},
                {"symbol": "TSLA", "name": "Tesla Inc.", "report_date": "2023-07-19", "time": "AMC", "estimate_eps": 0.82, "sector": "Consumer Cyclical"},
                {"symbol": "JPM", "name": "JPMorgan Chase", "report_date": "2023-07-14", "time": "BMO", "estimate_eps": 3.95, "sector": "Financial Services"},
                {"symbol": "BAC", "name": "Bank of America", "report_date": "2023-07-18", "time": "BMO", "estimate_eps": 0.84, "sector": "Financial Services"},
                {"symbol": "PG", "name": "Procter & Gamble", "report_date": "2023-07-28", "time": "BMO", "estimate_eps": 1.32, "sector": "Consumer Defensive"}
            ]
            
            # Filter by date range
            today = datetime.now().strftime("%Y-%m-%d")
            cutoff_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
            filtered_calendar = [c for c in calendar if today <= c["report_date"] <= cutoff_date]
            
            # Sort by date
            filtered_calendar = sorted(filtered_calendar, key=lambda x: x["report_date"])
            
            return filtered_calendar
            
        except Exception as e:
            logger.error(f"Error getting earnings calendar: {e}")
            return []

class MarketDataClient:
    """
    Client wrapper for the MarketDataAPI.
    """
    
    def __init__(self):
        """Initialize the market data client."""
        self.api = MarketDataAPI()
    
    def get_market_summary(self):
        """Get a summary of current market conditions."""
        return self.api.get_market_summary()
    
    def get_portfolio_exposure(self, region=None, sector=None):
        """Get portfolio exposure by region and sector."""
        return self.api.get_portfolio_exposure(region, sector)
    
    def get_earnings_surprises(self, days=30, sector=None):
        """Get recent earnings surprises."""
        return self.api.get_earnings_surprises(days, sector)
    
    def get_stock_data(self, symbol, interval="daily", full=False):
        """Get stock data for a symbol."""
        return self.api.get_stock_data(symbol, interval, full)
    
    def get_company_overview(self, symbol):
        """Get company overview data."""
        return self.api.get_company_overview(symbol)
    
    def get_earnings(self, symbol):
        """Get earnings data for a company."""
        return self.api.get_earnings(symbol)
    
    def get_sector_performance(self):
        """Get sector performance data."""
        return self.api.get_sector_performance()
    
    def get_earnings_calendar(self, days=7):
        """Get upcoming earnings calendar."""
        return self.api.get_earnings_calendar(days)
