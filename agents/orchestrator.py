"""
Orchestrator agent that coordinates between specialized agents.
"""
import os
import logging
from typing import Dict, List, Any, Optional
import json
from datetime import datetime

from agents.api_agent import APIAgent
from agents.scraping_agent import ScrapingAgent
from agents.retriever_agent import RetrieverAgent
from agents.analysis_agent import AnalysisAgent
from agents.language_agent import LanguageAgent
from agents.voice_agent import VoiceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates the flow between specialized agents to process financial queries.
    """
    
    def __init__(self, market_data_client, web_scraper, vector_store):
        """
        Initialize the orchestrator with data clients.
        
        Args:
            market_data_client: Client for market data
            web_scraper: Web scraper for financial data
            vector_store: Vector store for document retrieval
        """
        self.market_data_client = market_data_client
        self.web_scraper = web_scraper
        self.vector_store = vector_store
        
        # Initialize specialized agents
        self.api_agent = APIAgent(market_data_client)
        self.scraping_agent = ScrapingAgent(web_scraper)
        self.retriever_agent = RetrieverAgent(vector_store)
        self.analysis_agent = AnalysisAgent()
        self.language_agent = LanguageAgent()
        self.voice_agent = VoiceAgent()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def process_query(self, query: str) -> str:
        """
        Process a user query through the appropriate agents.
        
        Args:
            query: User's query text
            
        Returns:
            Response text
        """
        self.logger.info(f"Processing query: {query}")
        
        try:
            # Analyze the query to determine which agents to use
            query_type = self._analyze_query_type(query)
            
            # For portfolio exposure and earnings surprises queries, use the API agent
            if "portfolio" in query_type or "exposure" in query_type or "allocation" in query_type:
                return self._process_portfolio_query(query)
            elif "earnings" in query_type or "surprises" in query_type:
                return self._process_earnings_query(query)
            elif "market" in query_type or "overview" in query_type:
                return self._process_market_query(query)
            else:
                # For general queries, use a simple response
                return self._process_general_query(query)
        
        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            return f"I'm sorry, I encountered an error while processing your query: {str(e)}"
    
    def _analyze_query_type(self, query: str) -> str:
        """
        Analyze the query to determine its type.
        
        Args:
            query: User's query text
            
        Returns:
            Query type
        """
        query = query.lower()
        
        if any(keyword in query for keyword in ["portfolio", "exposure", "allocation", "holdings", "stocks", "tech stocks", "asia"]):
            return "portfolio"
        elif any(keyword in query for keyword in ["earnings", "surprises", "beat", "miss", "estimate"]):
            return "earnings"
        elif any(keyword in query for keyword in ["market", "indices", "index", "overview", "summary"]):
            return "market"
        else:
            return "general"
    
    def _process_portfolio_query(self, query: str) -> str:
        """
        Process a portfolio-related query.
        
        Args:
            query: User's query text
            
        Returns:
            Response text
        """
        self.logger.info("Processing portfolio query")
        
        # Extract region and sector from query
        region = None
        sector = None
        
        if "asia" in query.lower():
            region = "Asia"
        elif "north america" in query.lower() or "american" in query.lower():
            region = "North America"
        elif "europe" in query.lower() or "european" in query.lower():
            region = "Europe"
        
        if "tech" in query.lower() or "technology" in query.lower():
            sector = "Technology"
        elif "consumer" in query.lower():
            sector = "Consumer Cyclical"
        elif "energy" in query.lower():
            sector = "Energy"
        elif "financial" in query.lower():
            sector = "Financial Services"
        
        # Get portfolio data
        portfolio_data = self.api_agent.get_portfolio_exposure(region, sector)
        
        # Process the data through the analysis agent
        analysis = self.analysis_agent.analyze_portfolio(portfolio_data, query)
        
        # Generate a response using the language agent
        response = self.language_agent.generate_portfolio_response(analysis, query)
        
        return response
    
    def _process_earnings_query(self, query: str) -> str:
        """
        Process an earnings-related query.
        
        Args:
            query: User's query text
            
        Returns:
            Response text
        """
        self.logger.info("Processing earnings query")
        
        # Extract sector from query
        sector = None
        
        if "tech" in query.lower() or "technology" in query.lower():
            sector = "Technology"
        elif "consumer" in query.lower():
            sector = "Consumer Cyclical"
        elif "energy" in query.lower():
            sector = "Energy"
        elif "financial" in query.lower():
            sector = "Financial Services"
        
        # Get earnings data
        earnings_data = self.api_agent.get_earnings_surprises(30, sector)
        
        # Process the data through the analysis agent
        analysis = self.analysis_agent.analyze_earnings(earnings_data, query)
        
        # Generate a response using the language agent
        response = self.language_agent.generate_earnings_response(analysis, query)
        
        return response
    
    def _process_market_query(self, query: str) -> str:
        """
        Process a market-related query.
        
        Args:
            query: User's query text
            
        Returns:
            Response text
        """
        self.logger.info("Processing market query")
        
        # Get market data
        market_data = self.api_agent.get_market_summary()
        
        # Process the data through the analysis agent
        analysis = self.analysis_agent.analyze_market(market_data, query)
        
        # Generate a response using the language agent
        response = self.language_agent.generate_market_response(analysis, query)
        
        return response
    
    def _process_general_query(self, query: str) -> str:
        """
        Process a general query with a simple response.
        
        Args:
            query: User's query text
            
        Returns:
            Response text
        """
        self.logger.info("Processing general query")
        
        # For demonstration purposes, return a simple response
        return f"I understand you're asking about: {query}\n\nTo get specific financial information, try asking about market overview, portfolio exposure (especially in regions like Asia or sectors like Technology), or recent earnings surprises."
