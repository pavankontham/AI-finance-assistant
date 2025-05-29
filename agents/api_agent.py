"""
API agent for fetching market data.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import pandas as pd
import json
from datetime import datetime, timedelta

from agents.base_agent import BaseAgent
from data_ingestion.market_data import MarketDataAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIAgent(BaseAgent):
    """
    Agent for fetching market data from financial APIs.
    """
    
    def __init__(self, market_data_client=None, agent_id: str = "api_agent", agent_name: str = "API Agent"):
        """
        Initialize the API agent.
        
        Args:
            market_data_client: Optional market data client
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name for the agent
        """
        super().__init__(agent_id, agent_name)
        self.market_data_client = market_data_client
        self.market_data_api = MarketDataAPI()
    
    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process input data and return market data.
        
        Args:
            input_data: Dictionary containing input parameters
                - action: Action to perform (e.g., 'get_stock_data', 'get_company_overview')
                - parameters: Parameters for the action
            
        Returns:
            Dictionary containing market data
        """
        action = input_data.get('action', '')
        parameters = input_data.get('parameters', {})
        
        logger.info(f"Processing {action} with parameters: {parameters}")
        
        result = {}
        
        try:
            if action == 'get_stock_data':
                symbol = parameters.get('symbol', '')
                interval = parameters.get('interval', 'daily')
                full = parameters.get('full', False)
                
                if not symbol:
                    return {"error": "Symbol parameter is required"}
                
                result = self.market_data_api.get_stock_data(symbol, interval, full)
            
            elif action == 'get_company_overview':
                symbol = parameters.get('symbol', '')
                
                if not symbol:
                    return {"error": "Symbol parameter is required"}
                
                data = self.market_data_api.get_company_overview(symbol)
                result = data
            
            elif action == 'get_earnings':
                symbol = parameters.get('symbol', '')
                
                if not symbol:
                    return {"error": "Symbol parameter is required"}
                
                data = self.market_data_api.get_earnings(symbol)
                result = data
            
            elif action == 'get_sector_performance':
                data = self.market_data_api.get_sector_performance()
                result = {"sectors": data}
            
            elif action == 'get_portfolio_exposure':
                region = parameters.get('region')
                sector = parameters.get('sector')
                
                # Use the new portfolio exposure method
                result = self.market_data_api.get_portfolio_exposure(region, sector)
            
            elif action == 'get_earnings_surprises':
                days = parameters.get('days', 30)
                sector = parameters.get('sector')
                
                # Use the new earnings surprises method
                result = self.market_data_api.get_earnings_surprises(days, sector)
            
            elif action == 'get_market_summary':
                # Use the new market summary method
                result = self.market_data_api.get_market_summary()
            
            else:
                result = {"error": f"Unknown action: {action}"}
        
        except Exception as e:
            logger.error(f"Error processing {action}: {e}")
            result = {"error": str(e)}
        
        return result
    
    async def get_stock_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get the latest stock price for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary with price information
        """
        try:
            data = self.market_data_api.get_stock_data(symbol)
            
            if "quote" in data:
                return {
                    "symbol": symbol,
                    "price": data["quote"].get("price", 0.0),
                    "change": data["quote"].get("change", 0.0),
                    "change_percent": data["quote"].get("change_percent", 0.0),
                    "volume": data["quote"].get("volume", 0),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {"error": f"No data found for {symbol}"}
                
        except Exception as e:
            logger.error(f"Error getting stock price for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_market_data(self, query: str = "") -> Dict[str, Any]:
        """
        Get market data based on a query.
        
        Args:
            query: Query string to filter data
            
        Returns:
            Dictionary with market data
        """
        try:
            logger.info(f"Getting market data for query: {query}")
            
            # Extract symbols from query if present
            symbols = []
            query_lower = query.lower()
            
            # Check for common stock symbols and indices
            common_symbols = {
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
                "dow": "^DJI",
                "s&p": "^GSPC",
                "s&p 500": "^GSPC",
                "nasdaq": "^IXIC",
                "nikkei": "^N225",
                "hang seng": "^HSI",
                "ftse": "^FTSE",
                "dax": "^GDAXI"
            }
            
            # Extract symbols based on company/index names in query
            for name, symbol in common_symbols.items():
                if name in query_lower:
                    symbols.append(symbol)
            
            # If no specific symbols were found but query mentions markets or stocks, add major indices
            if not symbols and ("market" in query_lower or "stock" in query_lower or "index" in query_lower or "indices" in query_lower):
                symbols = ["^DJI", "^GSPC", "^IXIC"]  # Dow, S&P 500, NASDAQ
            
            # If we found specific symbols or need indices, get real-time data for them
            if symbols:
                # Import the web scraper to get real-time data
                from data_ingestion.web_scraper import WebScraper
                web_scraper = WebScraper()
                
                # Get real-time market data
                real_time_data = web_scraper.get_realtime_market_data(symbols)
                
                return {
                    "market_data": real_time_data,
                    "symbols": symbols,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                # Return a market summary if no specific symbols were mentioned
                return self.get_market_summary()
                
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
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
        try:
            logger.info(f"Getting portfolio exposure for region={region}, sector={sector}")
            
            # If market_data_client is available, use it
            if self.market_data_client:
                return self.market_data_client.get_portfolio_exposure(region, sector)
            
            # Otherwise use the API directly
            return self.market_data_api.get_portfolio_exposure(region, sector)
                
        except Exception as e:
            logger.error(f"Error getting portfolio exposure: {e}")
            return {"error": str(e)}
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current market conditions.
        
        Returns:
            Dictionary with market summary information
        """
        try:
            logger.info("Getting market summary")
            
            # If market_data_client is available, use it
            if self.market_data_client:
                return self.market_data_client.get_market_summary()
            
            # Otherwise use the API directly
            return self.market_data_api.get_market_summary()
                
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
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
        try:
            logger.info(f"Getting earnings surprises for days={days}, sector={sector}")
            
            # If market_data_client is available, use it
            if self.market_data_client:
                return self.market_data_client.get_earnings_surprises(days, sector)
            
            # Otherwise use the API directly
            return self.market_data_api.get_earnings_surprises(days, sector)
                
        except Exception as e:
            logger.error(f"Error getting earnings surprises: {e}")
            return {"error": str(e)}
    
    def get_earnings_data(self) -> Dict[str, Any]:
        """
        Get earnings data.
        
        Returns:
            Dictionary with earnings data
        """
        try:
            logger.info("Getting earnings data")
            
            # If market_data_client is available, use it
            if self.market_data_client:
                return self.market_data_client.get_earnings_calendar()
            
            # Otherwise use the API directly
            return self.market_data_api.get_earnings_calendar()
                
        except Exception as e:
            logger.error(f"Error getting earnings data: {e}")
            return {"error": str(e)}
    
    async def get_portfolio_analysis(self, region: Optional[str] = None, sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Get portfolio analysis.
        
        Args:
            region: Optional region to filter by
            sector: Optional sector to filter by
            
        Returns:
            Dictionary with portfolio analysis
        """
        try:
            logger.info(f"Getting portfolio analysis for region={region}, sector={sector}")
            
            # Get portfolio data
            portfolio_data = self.get_portfolio_exposure(region, sector)
            
            # Extract portfolio holdings
            holdings = portfolio_data.get("portfolio", [])
            
            # Calculate total value
            total_value = sum(holding.get("value", 0) for holding in holdings)
            
            # Calculate allocation by region and sector
            region_allocation = {}
            sector_allocation = {}
            
            for holding in holdings:
                r = holding.get("region", "Unknown")
                s = holding.get("sector", "Unknown")
                value = holding.get("value", 0)
                
                if r in region_allocation:
                    region_allocation[r] += value
                else:
                    region_allocation[r] = value
                    
                if s in sector_allocation:
                    sector_allocation[s] += value
                else:
                    sector_allocation[s] = value
            
            # Convert to percentages
            region_pct = {r: (v / total_value * 100) for r, v in region_allocation.items()}
            sector_pct = {s: (v / total_value * 100) for s, v in sector_allocation.items()}
            
            # Get top holdings
            top_holdings = sorted(holdings, key=lambda h: h.get("value", 0), reverse=True)[:5]
            
            return {
                "total_value": total_value,
                "num_holdings": len(holdings),
                "region_allocation": region_pct,
                "sector_allocation": sector_pct,
                "top_holdings": top_holdings,
                "timestamp": datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"Error getting portfolio analysis: {e}")
            return {"error": str(e)} 
