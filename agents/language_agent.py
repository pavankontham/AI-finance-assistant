"""
Language agent for generating natural language responses.
"""
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageAgent:
    """
    Agent for generating natural language responses from analysis results.
    """
    
    def __init__(self):
        """Initialize the language agent."""
        self.logger = logging.getLogger(__name__)
    
    def generate_portfolio_response(self, analysis: Dict[str, Any], query: str) -> str:
        """
        Generate a natural language response for portfolio analysis.
        
        Args:
            analysis: Dictionary with portfolio analysis results
            query: Original user query
            
        Returns:
            Natural language response
        """
        self.logger.info("Generating portfolio response")
        
        try:
            # Handle errors in analysis
            if "error" in analysis:
                return f"I'm sorry, I encountered an error analyzing your portfolio: {analysis['error']}"
            
            # Initialize response parts
            response_parts = []
            
            # Add portfolio overview
            total_value = analysis.get("total_value", 0)
            
            # Check if we have focus information (specific region/sector)
            if "focus_combined" in analysis and analysis["focus_combined"] == "Asia Technology":
                # This is an Asia tech query
                focus_pct = analysis.get("focus_percentage", 0)
                response_parts.append(f"Today, your Asia tech allocation is {focus_pct:.1f}% of your total portfolio value (${total_value:,.2f}).")
                
                # Add comparison to previous if available
                if "previous" in analysis and "focus_percentage" in analysis.get("previous", {}):
                    prev_pct = analysis["previous"]["focus_percentage"]
                    change = focus_pct - prev_pct
                    if abs(change) > 0.1:  # Only mention if change is significant
                        response_parts.append(f"This is {'up' if change > 0 else 'down'} from {prev_pct:.1f}% yesterday, a change of {abs(change):.1f} percentage points.")
                
                # Add top holdings
                if "focus_holdings" in analysis and analysis["focus_holdings"]:
                    top_holdings = analysis["focus_holdings"][:3]  # Top 3
                    holdings_text = ", ".join([f"{h.get('name', h.get('symbol', ''))} ({h.get('weight', 0):.1f}%)" for h in top_holdings])
                    response_parts.append(f"Top holdings in this segment: {holdings_text}.")
            
            elif "focus_region" in analysis:
                # This is a region-specific query
                region = analysis["focus_region"]
                focus_pct = analysis.get("focus_percentage", 0)
                response_parts.append(f"Your {region} allocation is {focus_pct:.1f}% of your total portfolio value (${total_value:,.2f}).")
                
                # Add sector breakdown for this region
                if "focus_sectors" in analysis:
                    sectors = analysis["focus_sectors"]
                    top_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:3]
                    sectors_text = ", ".join([f"{sector} ({pct:.1f}%)" for sector, pct in top_sectors])
                    response_parts.append(f"Top sectors in {region}: {sectors_text}.")
            
            elif "focus_sector" in analysis:
                # This is a sector-specific query
                sector = analysis["focus_sector"]
                focus_pct = analysis.get("focus_percentage", 0)
                response_parts.append(f"Your {sector} allocation is {focus_pct:.1f}% of your total portfolio value (${total_value:,.2f}).")
                
                # Add region breakdown for this sector
                if "focus_regions" in analysis:
                    regions = analysis["focus_regions"]
                    top_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:3]
                    regions_text = ", ".join([f"{region} ({pct:.1f}%)" for region, pct in top_regions])
                    response_parts.append(f"Top regions in {sector}: {regions_text}.")
            
            else:
                # General portfolio query
                response_parts.append(f"Your total portfolio value is ${total_value:,.2f}.")
                
                # Add sector allocation
                if "sector_allocation" in analysis:
                    sectors = analysis["sector_allocation"]
                    top_sectors = sorted(sectors.items(), key=lambda x: x[1], reverse=True)[:3]
                    sectors_text = ", ".join([f"{sector} ({pct:.1f}%)" for sector, pct in top_sectors])
                    response_parts.append(f"Top sectors: {sectors_text}.")
                
                # Add region allocation
                if "region_allocation" in analysis:
                    regions = analysis["region_allocation"]
                    top_regions = sorted(regions.items(), key=lambda x: x[1], reverse=True)[:3]
                    regions_text = ", ".join([f"{region} ({pct:.1f}%)" for region, pct in top_regions])
                    response_parts.append(f"Top regions: {regions_text}.")
            
            # Join all parts into a coherent response
            return " ".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating portfolio response: {e}")
            return "I'm sorry, I encountered an error while generating a response about your portfolio."
    
    def generate_earnings_response(self, analysis: Dict[str, Any], query: str) -> str:
        """
        Generate a natural language response for earnings analysis.
        
        Args:
            analysis: Dictionary with earnings analysis results
            query: Original user query
            
        Returns:
            Natural language response
        """
        self.logger.info("Generating earnings response")
        
        try:
            # Handle errors in analysis
            if "error" in analysis:
                return f"I'm sorry, I encountered an error analyzing earnings data: {analysis['error']}"
            
            # Initialize response parts
            response_parts = []
            
            # Check if we have focus information (specific sector)
            if "focus_sector" in analysis:
                sector = analysis["focus_sector"]
                
                # Add sector-specific beat rate
                if "focus_beat_rate" in analysis:
                    beat_rate = analysis["focus_beat_rate"]
                    response_parts.append(f"In the {sector} sector, {beat_rate:.1f}% of companies beat earnings expectations.")
                
                # Add specific company surprises
                if "focus_surprises" in analysis:
                    surprises = analysis["focus_surprises"]
                    
                    # Add top beats
                    beats = [s for s in surprises if s.get("surprise_percent", 0) > 0]
                    if beats:
                        beats_sorted = sorted(beats, key=lambda x: x.get("surprise_percent", 0), reverse=True)[:2]
                        for beat in beats_sorted:
                            company = beat.get("name", beat.get("symbol", ""))
                            pct = beat.get("surprise_percent", 0)
                            response_parts.append(f"{company} beat estimates by {pct:.1f}%.")
                    
                    # Add top misses
                    misses = [s for s in surprises if s.get("surprise_percent", 0) < 0]
                    if misses:
                        misses_sorted = sorted(misses, key=lambda x: x.get("surprise_percent", 0))[:2]
                        for miss in misses_sorted:
                            company = miss.get("name", miss.get("symbol", ""))
                            pct = abs(miss.get("surprise_percent", 0))
                            response_parts.append(f"{company} missed estimates by {pct:.1f}%.")
            else:
                # General earnings query
                total = analysis.get("total_surprises", 0)
                positive = analysis.get("positive_surprises", 0)
                
                if total > 0:
                    beat_rate = (positive / total) * 100
                    response_parts.append(f"Overall, {beat_rate:.1f}% of companies beat earnings expectations.")
                
                # Add top beats
                if "top_beats" in analysis and analysis["top_beats"]:
                    top_beat = analysis["top_beats"][0]
                    company = top_beat.get("name", top_beat.get("symbol", ""))
                    pct = top_beat.get("surprise_percent", 0)
                    response_parts.append(f"The biggest positive surprise was {company}, which beat estimates by {pct:.1f}%.")
                
                # Add top misses
                if "top_misses" in analysis and analysis["top_misses"]:
                    top_miss = analysis["top_misses"][0]
                    company = top_miss.get("name", top_miss.get("symbol", ""))
                    pct = abs(top_miss.get("surprise_percent", 0))
                    response_parts.append(f"The biggest negative surprise was {company}, which missed estimates by {pct:.1f}%.")
            
            # Join all parts into a coherent response
            return " ".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating earnings response: {e}")
            return "I'm sorry, I encountered an error while generating a response about earnings surprises."
    
    def generate_market_response(self, analysis: Dict[str, Any], query: str) -> str:
        """
        Generate a natural language response for market analysis.
        
        Args:
            analysis: Dictionary with market analysis results
            query: Original user query
            
        Returns:
            Natural language response
        """
        self.logger.info("Generating market response")
        
        try:
            # Handle errors in analysis
            if "error" in analysis:
                return f"I'm sorry, I encountered an error analyzing market data: {analysis['error']}"
            
            # Initialize response parts
            response_parts = []
            
            # Add market sentiment
            if "market_sentiment" in analysis:
                sentiment = analysis["market_sentiment"]
                response_parts.append(f"Overall market sentiment today is {sentiment}.")
            
            # Check if we have focus information (specific region)
            if "focus_region" in analysis:
                region = analysis["focus_region"]
                
                # Add region-specific indices
                if "focus_indices" in analysis:
                    indices = analysis["focus_indices"]
                    for name, data in indices.items():
                        change_pct = data.get("change_percent", 0)
                        direction = "up" if change_pct > 0 else "down"
                        response_parts.append(f"{name} is {direction} {abs(change_pct):.2f}% today.")
            
            # Check if we have focus information (specific sector)
            elif "focus_sector" in analysis:
                sector = analysis["focus_sector"]
                
                # Add sector-specific performance
                if "focus_sector_performance" in analysis:
                    perf = analysis["focus_sector_performance"]
                    direction = "up" if perf > 0 else "down"
                    response_parts.append(f"The {sector} sector is {direction} {abs(perf):.2f}% today.")
            
            else:
                # General market query
                # Add key indices
                if "indices_performance" in analysis:
                    indices = analysis["indices_performance"]
                    major_indices = ["S&P 500", "Dow Jones", "NASDAQ"]
                    
                    for idx_name in major_indices:
                        for name, data in indices.items():
                            if idx_name.lower() in name.lower():
                                change_pct = data.get("change_percent", 0)
                                direction = "up" if change_pct > 0 else "down"
                                response_parts.append(f"{name} is {direction} {abs(change_pct):.2f}% today.")
                                break
                
                # Add top and bottom sectors
                if "sector_performance" in analysis and analysis["sector_performance"]:
                    sectors = analysis["sector_performance"]
                    
                    # Top sector
                    top_sector = max(sectors.items(), key=lambda x: x[1])
                    response_parts.append(f"The best performing sector is {top_sector[0]} ({top_sector[1]:.2f}%).")
                    
                    # Bottom sector
                    bottom_sector = min(sectors.items(), key=lambda x: x[1])
                    response_parts.append(f"The worst performing sector is {bottom_sector[0]} ({bottom_sector[1]:.2f}%).")
            
            # Join all parts into a coherent response
            return " ".join(response_parts)
            
        except Exception as e:
            self.logger.error(f"Error generating market response: {e}")
            return "I'm sorry, I encountered an error while generating a response about market conditions."
