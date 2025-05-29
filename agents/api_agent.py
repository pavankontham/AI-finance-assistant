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
    
    def __init__(self, agent_id: str = "api_agent", agent_name: str = "API Agent"):
        """
        Initialize the API agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name for the agent
        """
        super().__init__(agent_id, agent_name)
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
                
                # Format the data for the response
                formatted_data = {}
                for symbol, data in real_time_data.items():
                    formatted_data[symbol] = {
                        "symbol": symbol,
                        "name": data.get("name", ""),
                        "price": data.get("price", 0.0),
                        "change": data.get("change", 0.0),
                        "change_percent": data.get("change_percent", 0.0),
                        "volume": data.get("volume", 0),
                        "market_cap": data.get("market_cap", ""),
                        "pe_ratio": data.get("pe_ratio", None),
                        "source": data.get("source", "Real-time Data"),
                        "timestamp": data.get("timestamp", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    }
                
                return {
                    "success": True,
                    "data": {
                        "stocks": formatted_data,
                        "query": query,
                        "data_source": "Real-time market data"
                    }
                }
            
            # If no specific symbols found, get general market data
            # First try to get real-time data for major indices
            from data_ingestion.web_scraper import WebScraper
            web_scraper = WebScraper()
            
            # Get real-time data for major indices
            indices = ["^DJI", "^GSPC", "^IXIC", "^N225", "^HSI", "^FTSE"]
            indices_data = web_scraper.get_realtime_market_data(indices)
            
            # Get sector performance from Alpha Vantage
            sector_performance = self.market_data_api.get_sector_performance()
            
            # Format the response
            market_summary = {
                "indices": {},
                "sectors": sector_performance,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_source": "Real-time market data"
            }
            
            # Add indices data
            for symbol, data in indices_data.items():
                index_name = {
                    "^DJI": "Dow Jones Industrial Average",
                    "^GSPC": "S&P 500",
                    "^IXIC": "NASDAQ Composite",
                    "^N225": "Nikkei 225",
                    "^HSI": "Hang Seng Index",
                    "^FTSE": "FTSE 100"
                }.get(symbol, data.get("name", symbol))
                
                market_summary["indices"][symbol] = {
                    "name": index_name,
                    "price": data.get("price", 0.0),
                    "change": data.get("change", 0.0),
                    "change_percent": data.get("change_percent", 0.0),
                    "source": data.get("source", "Real-time Data")
                }
            
            # Filter based on query if provided
            if query:
                # Check for region mentions
                regions = {
                    "asia": ["^N225", "^HSI"],  # Nikkei, Hang Seng
                    "europe": ["^FTSE", "^GDAXI"],  # FTSE, DAX
                    "us": ["^DJI", "^GSPC", "^IXIC"]  # Dow, S&P, NASDAQ
                }
                
                for region, indices_list in regions.items():
                    if region in query_lower:
                        # Filter indices to only include those from this region
                        filtered_indices = {symbol: data for symbol, data in market_summary["indices"].items() if symbol in indices_list}
                        market_summary["indices"] = filtered_indices
                        break
                
                # Check for sector mentions
                sectors = ["technology", "healthcare", "financials", "energy", "consumer", "utilities", "materials", "industrials", "real estate", "communication"]
                
                for sector in sectors:
                    if sector in query_lower:
                        # Filter sectors to only include the mentioned sector
                        if sector in market_summary["sectors"]:
                            market_summary["sectors"] = {sector: market_summary["sectors"][sector]}
                        break
            
            return {
                "success": True,
                "data": market_summary
            }
            
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            
            # Return a fallback response on error
            return {
                "success": False,
                "error": str(e),
                "data": {
                    "message": "Unable to retrieve real-time market data. Please try again later."
                }
            }
    
    def get_portfolio_data(self, region: str = None, sector: str = None) -> Dict[str, Any]:
        """
        Get portfolio data with optional filtering by region or sector.
        
        Args:
            region: Optional region filter
            sector: Optional sector filter
            
        Returns:
            Dictionary with portfolio data
        """
        try:
            logger.info(f"Getting portfolio data for region: {region}, sector: {sector}")
            
            # Get portfolio exposure data
            exposure_data = self.market_data_api.get_portfolio_exposure(region, sector)
            
            # Get performance data for portfolio holdings
            holdings = exposure_data.get("portfolio", [])
            for holding in holdings:
                symbol = holding.get("symbol")
                if symbol:
                    try:
                        stock_data = self.market_data_api.get_stock_data(symbol)
                        if stock_data and "quote" in stock_data:
                            holding["price"] = stock_data["quote"].get("price", 0.0)
                            holding["change"] = stock_data["quote"].get("change", 0.0)
                            holding["change_percent"] = stock_data["quote"].get("change_percent", 0.0)
                    except Exception as e:
                        logger.warning(f"Could not get data for {symbol}: {e}")
            
            return {
                "success": True,
                "analysis": {
                    "region_allocation": exposure_data.get("region_allocation", {}),
                    "sector_allocation": exposure_data.get("sector_allocation", {}),
                    "holdings": holdings,
                    "previous": exposure_data.get("previous", {})
                }
            }
                
        except Exception as e:
            logger.error(f"Error getting portfolio data: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive market summary.
        
        Returns:
            Dictionary with market summary
        """
        try:
            logger.info("Getting market summary")
            
            # Get market summary data
            summary_data = self.market_data_api.get_market_summary()
            
            # Get sector performance
            sector_performance = self.market_data_api.get_sector_performance()
            
            return {
                "success": True,
                "analysis": {
                    "indices_performance": summary_data.get("indices", {}),
                    "sector_performance": sector_performance,
                    "currencies": summary_data.get("currencies", {}),
                    "commodities": summary_data.get("commodities", {}),
                    "summary": summary_data.get("summary", "Market data unavailable.")
                }
            }
                
        except Exception as e:
            logger.error(f"Error getting market summary: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    def get_earnings_data(self) -> Dict[str, Any]:
        """
        Get recent earnings data.
        
        Returns:
            Dictionary with earnings data
        """
        try:
            logger.info("Getting earnings data")
            
            # Get earnings surprises for the past 30 days
            earnings_data = self.market_data_api.get_earnings_surprises(30)
            
            # Get upcoming earnings calendar
            calendar_data = self.market_data_api.get_earnings_calendar()
            
            return {
                "success": True,
                "analysis": {
                    "surprises": earnings_data.get("surprises", []),
                    "upcoming": calendar_data.get("earnings", [])
                }
            }
                
        except Exception as e:
            logger.error(f"Error getting earnings data: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    def get_earnings_surprises(self, region: str = None, sector: str = None) -> Dict[str, Any]:
        """
        Get earnings surprises with optional filtering by region or sector.
        
        Args:
            region: Optional region filter
            sector: Optional sector filter
            
        Returns:
            Dictionary with earnings surprises
        """
        try:
            logger.info(f"Getting earnings surprises for region: {region}, sector: {sector}")
            
            # Get earnings surprises for the past 30 days
            earnings_data = self.market_data_api.get_earnings_surprises(30)
            surprises = earnings_data.get("surprises", [])
            
            # Filter by region and sector if provided
            if region or sector:
                filtered_surprises = []
                for surprise in surprises:
                    if region and surprise.get("region") != region:
                        continue
                    if sector and surprise.get("sector") != sector:
                        continue
                    filtered_surprises.append(surprise)
                surprises = filtered_surprises
            
            return {
                "success": True,
                "analysis": {
                    "surprises": surprises
                }
            }
                
        except Exception as e:
            logger.error(f"Error getting earnings surprises: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": {}
            }
    
    async def get_portfolio_analysis(self, region: Optional[str] = None, sector: Optional[str] = None) -> Dict[str, Any]:
        """
        Get portfolio analysis for specific region or sector.
        
        Args:
            region: Optional region to filter by
            sector: Optional sector to filter by
            
        Returns:
            Dictionary with portfolio analysis
        """
        try:
            # Get portfolio exposure
            exposure_data = self.market_data_api.get_portfolio_exposure(region, sector)
            
            # Get earnings surprises for the portfolio
            portfolio_symbols = [item["symbol"] for item in exposure_data.get("portfolio", [])]
            
            # Get earnings surprises for relevant sector
            earnings_data = self.market_data_api.get_earnings_surprises(30, sector)
            
            # Get market summary
            market_data = self.market_data_api.get_market_summary()
            
            # Combine the data
            result = {
                "exposure": exposure_data,
                "earnings": earnings_data,
                "market": market_data,
                "timestamp": datetime.now().isoformat()
            }
            
            return result
                
        except Exception as e:
            logger.error(f"Error getting portfolio analysis: {e}")
            return {"error": str(e)} 