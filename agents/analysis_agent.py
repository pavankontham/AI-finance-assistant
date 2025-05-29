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
    
    def analyze_market(self, market_data, query=None):
        """
        Analyze market data to extract insights.
        
        Args:
            market_data: Market data including indices, sectors, etc.
            query: Optional query string to focus the analysis
            
        Returns:
            Dictionary with market analysis results
        """
        logger.info("Analyzing market data...")
        
        try:
            # Extract market metrics
            results = {
                "indices_performance": {},
                "sector_performance": {},
                "market_sentiment": "",
                "key_insights": []
            }
            
            # Process indices performance
            indices = market_data.get("indices", [])
            for index in indices:
                name = index.get("name", "Unknown")
                results["indices_performance"][name] = {
                    "price": index.get("price", 0),
                    "change": index.get("change", 0),
                    "change_percent": index.get("change_percent", 0)
                }
            
            # Process sector performance
            results["sector_performance"] = market_data.get("sectors", {})
            
            # Determine overall market sentiment
            positive_sectors = sum(1 for _, perf in results["sector_performance"].items() if perf > 0)
            total_sectors = len(results["sector_performance"])
            positive_indices = sum(1 for _, data in results["indices_performance"].items() if data.get("change_percent", 0) > 0)
            total_indices = len(results["indices_performance"])
            
            if positive_sectors > total_sectors * 0.7 and positive_indices > total_indices * 0.7:
                results["market_sentiment"] = "strongly bullish"
            elif positive_sectors > total_sectors * 0.5 and positive_indices > total_indices * 0.5:
                results["market_sentiment"] = "bullish"
            elif positive_sectors < total_sectors * 0.3 and positive_indices < total_indices * 0.3:
                results["market_sentiment"] = "strongly bearish"
            elif positive_sectors < total_sectors * 0.5 and positive_indices < total_indices * 0.5:
                results["market_sentiment"] = "bearish"
            else:
                results["market_sentiment"] = "neutral"
            
            # Generate key insights
            results["key_insights"] = [
                f"Overall market sentiment is {results['market_sentiment']}.",
                f"{positive_indices} out of {total_indices} major indices are positive today.",
                f"{positive_sectors} out of {total_sectors} sectors are showing positive performance."
            ]
            
            # Add top performing sector
            if results["sector_performance"]:
                top_sector = max(results["sector_performance"].items(), key=lambda x: x[1])
                results["key_insights"].append(f"The top performing sector is {top_sector[0]} at {top_sector[1]:.2f}%.")
            
            # Add worst performing sector
            if results["sector_performance"]:
                bottom_sector = min(results["sector_performance"].items(), key=lambda x: x[1])
                results["key_insights"].append(f"The worst performing sector is {bottom_sector[0]} at {bottom_sector[1]:.2f}%.")
            
            # Focus analysis based on query if provided
            if query:
                query_lower = query.lower()
                
                # Check for region focus
                if "asia" in query_lower:
                    results["focus_region"] = "Asia"
                    # Filter indices for Asian markets
                    asia_indices = {name: data for name, data in results["indices_performance"].items() 
                                  if "nikkei" in name.lower() or "hang seng" in name.lower() or "shanghai" in name.lower()}
                    results["focus_indices"] = asia_indices
                
                # Check for sector focus
                if "tech" in query_lower or "technology" in query_lower:
                    results["focus_sector"] = "Technology"
                    # Extract technology sector performance
                    if "Technology" in results["sector_performance"]:
                        results["focus_sector_performance"] = results["sector_performance"]["Technology"]
            
            logger.info("Market analysis completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing market data: {e}")
            return {
                "error": f"Error analyzing market data: {str(e)}"
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
    
    def generate_market_brief(self, query, portfolio_data=None, market_data=None, earnings_data=None):
        """
        Generate a comprehensive market brief based on available data.
        
        Args:
            query: Query string to focus the brief
            portfolio_data: Optional portfolio data
            market_data: Optional market data
            earnings_data: Optional earnings data
            
        Returns:
            Dictionary with market brief
        """
        logger.info(f"Generating market brief for query: {query}")
        
        try:
            # Initialize results
            results = {
                "summary": "",
                "portfolio_insights": [],
                "market_insights": [],
                "earnings_insights": [],
                "recommendations": []
            }
            
            # Analyze portfolio data if available
            if portfolio_data:
                portfolio_analysis = self.analyze_portfolio(portfolio_data, query)
                
                # Extract portfolio insights
                if "focus_combined" in portfolio_analysis and portfolio_analysis["focus_combined"] == "Asia Technology":
                    asia_tech_pct = portfolio_analysis.get("focus_percentage", 0)
                    results["portfolio_insights"].append(f"Your Asia tech allocation is {asia_tech_pct:.1f}% of total portfolio.")
                    
                    # Compare to previous if available
                    if "previous" in portfolio_data and "asia_tech_percentage" in portfolio_data["previous"]:
                        prev_pct = portfolio_data["previous"]["asia_tech_percentage"]
                        change = asia_tech_pct - prev_pct
                        results["portfolio_insights"].append(f"This is {'up' if change > 0 else 'down'} from {prev_pct:.1f}% yesterday, a change of {abs(change):.1f} percentage points.")
                
                # Add top holdings in focus area
                if "focus_holdings" in portfolio_analysis and portfolio_analysis["focus_holdings"]:
                    top_holdings = portfolio_analysis["focus_holdings"][:3]  # Top 3
                    holdings_text = ", ".join([f"{h.get('name', h.get('symbol', ''))} ({h.get('weight', 0):.1f}%)" for h in top_holdings])
                    results["portfolio_insights"].append(f"Top holdings in this segment: {holdings_text}.")
            
            # Analyze market data if available
            if market_data:
                market_analysis = self.analyze_market(market_data, query)
                
                # Extract market insights
                if "market_sentiment" in market_analysis:
                    results["market_insights"].append(f"Overall market sentiment is {market_analysis['market_sentiment']}.")
                
                # Add focused insights
                if "focus_region" in market_analysis and market_analysis["focus_region"] == "Asia":
                    if "focus_indices" in market_analysis:
                        for name, data in market_analysis["focus_indices"].items():
                            results["market_insights"].append(f"{name} is {data.get('change_percent', 0):.2f}% today.")
            
            # Analyze earnings data if available
            if earnings_data:
                earnings_analysis = self.analyze_earnings(earnings_data, query)
                
                # Extract earnings insights
                if "focus_sector" in earnings_analysis and earnings_analysis["focus_sector"] == "Technology":
                    if "focus_beat_rate" in earnings_analysis:
                        results["earnings_insights"].append(f"In the Technology sector, {earnings_analysis['focus_beat_rate']}% of companies beat expectations.")
                    
                    # Add specific company surprises
                    if "focus_surprises" in earnings_analysis:
                        for surprise in earnings_analysis["focus_surprises"][:3]:  # Top 3
                            company = surprise.get("name", surprise.get("symbol", ""))
                            pct = surprise.get("surprise_percent", 0)
                            if pct > 0:
                                results["earnings_insights"].append(f"{company} beat estimates by {pct:.1f}%.")
                            else:
                                results["earnings_insights"].append(f"{company} missed estimates by {abs(pct):.1f}%.")
            
            # Generate overall summary
            summary_parts = []
            
            if portfolio_data and "focus_percentage" in portfolio_analysis:
                summary_parts.append(f"Your Asia tech allocation is {portfolio_analysis.get('focus_percentage', 0):.1f}% of AUM")
            
            if earnings_data and "focus_surprises" in earnings_analysis:
                beats = [s for s in earnings_analysis["focus_surprises"] if s.get("surprise_percent", 0) > 0]
                misses = [s for s in earnings_analysis["focus_surprises"] if s.get("surprise_percent", 0) < 0]
                
                if beats:
                    top_beat = beats[0]
                    summary_parts.append(f"{top_beat.get('name', top_beat.get('symbol', ''))} beat estimates by {top_beat.get('surprise_percent', 0):.1f}%")
                
                if misses:
                    top_miss = misses[0]
                    summary_parts.append(f"{top_miss.get('name', top_miss.get('symbol', ''))} missed by {abs(top_miss.get('surprise_percent', 0)):.1f}%")
            
            if market_data and "market_sentiment" in market_analysis:
                summary_parts.append(f"Regional sentiment is {market_analysis['market_sentiment']}")
            
            results["summary"] = ". ".join(summary_parts) + "."
            
            logger.info("Market brief generated successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error generating market brief: {e}")
            return {
                "error": f"Error generating market brief: {str(e)}"
            }

# Example usage
if __name__ == "__main__":
    agent = AnalysisAgent()
    
    # Sample portfolio data
    portfolio_data = {
        "holdings": [
            {"symbol": "AAPL", "name": "Apple Inc.", "value": 10000, "sector": "Technology", "region": "North America"},
            {"symbol": "TSM", "name": "Taiwan Semiconductor", "value": 5000, "sector": "Technology", "region": "Asia"},
            {"symbol": "9988.HK", "name": "Alibaba Group", "value": 3000, "sector": "Technology", "region": "Asia"},
            {"symbol": "MSFT", "name": "Microsoft Corp.", "value": 8000, "sector": "Technology", "region": "North America"}
        ],
        "volatility": 0.15,
        "beta": 1.1,
        "sharpe_ratio": 0.85,
        "daily_return": 0.25,
        "weekly_return": 1.5,
        "monthly_return": 2.8
    }
    
    # Test portfolio analysis
    portfolio_analysis = agent.analyze_portfolio(portfolio_data)
    print(f"Portfolio Analysis: {json.dumps(portfolio_analysis, indent=2)}")
