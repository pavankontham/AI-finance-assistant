"""
Analysis agent for financial data processing and insights.
"""
import os
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Agent for analyzing financial data and generating insights.
    """
    
    def __init__(self):
        """Initialize the analysis agent."""
        self.agent_id = "analysis_agent"
    
    def analyze_portfolio(self, portfolio_data, query=None):
        """
        Analyze portfolio data to extract insights.
        
        Args:
            portfolio_data: Portfolio data including holdings, allocations, etc.
            query: Optional query string to focus the analysis
            
        Returns:
            Dictionary with portfolio analysis results
        """
        logger.info("Analyzing portfolio data...")
        
        try:
            # Extract portfolio metrics
            results = {
                "total_value": 0,
                "sector_allocation": {},
                "region_allocation": {},
                "top_holdings": [],
                "risk_metrics": {},
                "performance": {}
            }
            
            # Calculate total portfolio value
            total_value = 0
            for holding in portfolio_data.get("portfolio", []):
                value = holding.get("value", 0)
                total_value += value
            
            results["total_value"] = total_value
            
            # Extract existing sector and region allocations if available
            if "sector_allocation" in portfolio_data:
                results["sector_allocation"] = portfolio_data["sector_allocation"]
            else:
                # Calculate sector allocation
                sector_allocation = {}
                for holding in portfolio_data.get("portfolio", []):
                    sector = holding.get("sector", "Unknown")
                    value = holding.get("value", 0)
                    if sector in sector_allocation:
                        sector_allocation[sector] += value
                    else:
                        sector_allocation[sector] = value
                
                # Convert to percentages
                for sector, value in sector_allocation.items():
                    sector_allocation[sector] = round((value / total_value) * 100, 2) if total_value > 0 else 0
                
                results["sector_allocation"] = sector_allocation
            
            # Extract existing region allocation if available
            if "region_allocation" in portfolio_data:
                results["region_allocation"] = portfolio_data["region_allocation"]
            else:
                # Calculate region allocation
                region_allocation = {}
                for holding in portfolio_data.get("portfolio", []):
                    region = holding.get("region", "Unknown")
                    value = holding.get("value", 0)
                    if region in region_allocation:
                        region_allocation[region] += value
                    else:
                        region_allocation[region] = value
                
                # Convert to percentages
                for region, value in region_allocation.items():
                    region_allocation[region] = round((value / total_value) * 100, 2) if total_value > 0 else 0
                
                results["region_allocation"] = region_allocation
            
            # Get top holdings
            top_holdings = sorted(
                portfolio_data.get("portfolio", []),
                key=lambda x: x.get("value", 0),
                reverse=True
            )[:5]  # Top 5 holdings
            
            results["top_holdings"] = [
                {
                    "symbol": holding.get("symbol", ""),
                    "name": holding.get("name", ""),
                    "value": holding.get("value", 0),
                    "weight": round((holding.get("value", 0) / total_value) * 100, 2) if total_value > 0 else 0,
                    "sector": holding.get("sector", ""),
                    "region": holding.get("region", "")
                }
                for holding in top_holdings
            ]
            
            # Focus analysis based on query if provided
            if query:
                query_lower = query.lower()
                
                # Check for region focus
                if "asia" in query_lower:
                    results["focus_region"] = "Asia"
                    # Filter holdings by Asia region
                    asia_holdings = [h for h in portfolio_data.get("portfolio", []) if h.get("region") == "Asia"]
                    asia_value = sum(h.get("value", 0) for h in asia_holdings)
                    results["focus_value"] = asia_value
                    results["focus_percentage"] = round((asia_value / total_value) * 100, 2) if total_value > 0 else 0
                    results["focus_holdings"] = sorted(asia_holdings, key=lambda x: x.get("value", 0), reverse=True)
                    
                    # Calculate sector breakdown within Asia
                    asia_sectors = {}
                    for holding in asia_holdings:
                        sector = holding.get("sector", "Unknown")
                        value = holding.get("value", 0)
                        if sector in asia_sectors:
                            asia_sectors[sector] += value
                        else:
                            asia_sectors[sector] = value
                    
                    # Convert to percentages
                    for sector, value in asia_sectors.items():
                        asia_sectors[sector] = round((value / asia_value) * 100, 2) if asia_value > 0 else 0
                    
                    results["focus_sectors"] = asia_sectors
                
                # Check for sector focus
                if "tech" in query_lower or "technology" in query_lower:
                    results["focus_sector"] = "Technology"
                    # Filter holdings by Technology sector
                    tech_holdings = [h for h in portfolio_data.get("portfolio", []) if h.get("sector") == "Technology"]
                    tech_value = sum(h.get("value", 0) for h in tech_holdings)
                    results["focus_value"] = tech_value
                    results["focus_percentage"] = round((tech_value / total_value) * 100, 2) if total_value > 0 else 0
                    results["focus_holdings"] = sorted(tech_holdings, key=lambda x: x.get("value", 0), reverse=True)
                    
                    # Calculate region breakdown within Technology
                    tech_regions = {}
                    for holding in tech_holdings:
                        region = holding.get("region", "Unknown")
                        value = holding.get("value", 0)
                        if region in tech_regions:
                            tech_regions[region] += value
                        else:
                            tech_regions[region] = value
                    
                    # Convert to percentages
                    for region, value in tech_regions.items():
                        tech_regions[region] = round((value / tech_value) * 100, 2) if tech_value > 0 else 0
                    
                    results["focus_regions"] = tech_regions
                
                # Check for combined focus (Asia tech)
                if "asia" in query_lower and ("tech" in query_lower or "technology" in query_lower):
                    results["focus_combined"] = "Asia Technology"
                    # Filter holdings by Asia region and Technology sector
                    asia_tech_holdings = [
                        h for h in portfolio_data.get("portfolio", []) 
                        if h.get("region") == "Asia" and h.get("sector") == "Technology"
                    ]
                    asia_tech_value = sum(h.get("value", 0) for h in asia_tech_holdings)
                    results["focus_value"] = asia_tech_value
                    results["focus_percentage"] = round((asia_tech_value / total_value) * 100, 2) if total_value > 0 else 0
                    results["focus_holdings"] = sorted(asia_tech_holdings, key=lambda x: x.get("value", 0), reverse=True)
                
                # Check for risk focus
                if "risk" in query_lower or "exposure" in query_lower:
                    results["focus_risk"] = True
                    # In a real implementation, this would include more detailed risk metrics
            
            logger.info("Portfolio analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return {
                "error": f"Error analyzing portfolio: {str(e)}"
            }
    
    def analyze_earnings(self, earnings_data, query=None):
        """
        Analyze earnings data to extract insights.
        
        Args:
            earnings_data: Earnings data including surprises, upcoming reports, etc.
            query: Optional query string to focus the analysis
            
        Returns:
            Dictionary with earnings analysis results
        """
        logger.info("Analyzing earnings data...")
        
        try:
            # Extract earnings metrics
            results = {
                "total_surprises": 0,
                "positive_surprises": 0,
                "negative_surprises": 0,
                "top_beats": [],
                "top_misses": [],
                "sector_performance": {},
                "key_insights": []
            }
            
            # Process earnings surprises
            surprises = earnings_data.get("surprises", [])
            results["total_surprises"] = len(surprises)
            
            # Count positive and negative surprises
            for surprise in surprises:
                if surprise.get("surprise_percent", 0) > 0:
                    results["positive_surprises"] += 1
                else:
                    results["negative_surprises"] += 1
            
            # Get top beats
            top_beats = sorted(
                [s for s in surprises if s.get("surprise_percent", 0) > 0],
                key=lambda x: x.get("surprise_percent", 0),
                reverse=True
            )[:5]  # Top 5 beats
            
            results["top_beats"] = [
                {
                    "symbol": beat.get("symbol", ""),
                    "name": beat.get("name", ""),
                    "surprise_percent": beat.get("surprise_percent", 0),
                    "expected_eps": beat.get("expected_eps", 0),
                    "actual_eps": beat.get("actual_eps", 0),
                    "sector": beat.get("sector", "")
                }
                for beat in top_beats
            ]
            
            # Get top misses
            top_misses = sorted(
                [s for s in surprises if s.get("surprise_percent", 0) < 0],
                key=lambda x: x.get("surprise_percent", 0)
            )[:5]  # Top 5 misses
            
            results["top_misses"] = [
                {
                    "symbol": miss.get("symbol", ""),
                    "name": miss.get("name", ""),
                    "surprise_percent": miss.get("surprise_percent", 0),
                    "expected_eps": miss.get("expected_eps", 0),
                    "actual_eps": miss.get("actual_eps", 0),
                    "sector": miss.get("sector", "")
                }
                for miss in top_misses
            ]
            
            # Calculate sector performance in earnings
            sector_performance = {}
            for surprise in surprises:
                sector = surprise.get("sector", "Unknown")
                surprise_pct = surprise.get("surprise_percent", 0)
                
                if sector not in sector_performance:
                    sector_performance[sector] = {
                        "count": 0,
                        "positive": 0,
                        "negative": 0,
                        "total_surprise": 0
                    }
                
                sector_performance[sector]["count"] += 1
                if surprise_pct > 0:
                    sector_performance[sector]["positive"] += 1
                else:
                    sector_performance[sector]["negative"] += 1
                sector_performance[sector]["total_surprise"] += surprise_pct
            
            # Calculate average surprise by sector
            for sector, data in sector_performance.items():
                if data["count"] > 0:
                    data["average_surprise"] = round(data["total_surprise"] / data["count"], 2)
                    data["beat_rate"] = round((data["positive"] / data["count"]) * 100, 2)
            
            results["sector_performance"] = sector_performance
            
            # Generate key insights
            if results["total_surprises"] > 0:
                beat_rate = round((results["positive_surprises"] / results["total_surprises"]) * 100, 2)
                results["key_insights"].append(f"{beat_rate}% of companies beat earnings expectations.")
            
            if top_beats:
                top_beat = top_beats[0]
                results["key_insights"].append(
                    f"{top_beat.get('name', top_beat.get('symbol', ''))} had the largest positive surprise at {top_beat.get('surprise_percent', 0):.2f}%."
                )
            
            if top_misses:
                top_miss = top_misses[0]
                results["key_insights"].append(
                    f"{top_miss.get('name', top_miss.get('symbol', ''))} had the largest negative surprise at {top_miss.get('surprise_percent', 0):.2f}%."
                )
            
            # Focus analysis based on query if provided
            if query:
                query_lower = query.lower()
                
                # Check for sector focus
                if "tech" in query_lower or "technology" in query_lower:
                    results["focus_sector"] = "Technology"
                    # Filter surprises for Technology sector
                    tech_surprises = [s for s in surprises if s.get("sector") == "Technology"]
                    results["focus_surprises"] = tech_surprises
                    
                    # Calculate Technology sector metrics
                    if tech_surprises:
                        tech_positive = sum(1 for s in tech_surprises if s.get("surprise_percent", 0) > 0)
                        tech_beat_rate = round((tech_positive / len(tech_surprises)) * 100, 2)
                        results["focus_beat_rate"] = tech_beat_rate
                        results["key_insights"].append(f"In the Technology sector, {tech_beat_rate}% of companies beat expectations.")
                
                # Check for region focus
                if "asia" in query_lower:
                    results["focus_region"] = "Asia"
                    # Filter surprises for Asian companies
                    # This would require region data in the earnings surprises, which might not be available
                    # In a real implementation, you would need to join with company metadata
            
            logger.info("Earnings analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing earnings data: {e}")
            return {
                "error": f"Error analyzing earnings data: {str(e)}"
            }
