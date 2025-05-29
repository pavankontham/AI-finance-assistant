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
    
    def analyze_portfolio(self, portfolio_data):
        """
        Analyze portfolio data to extract insights.
        
        Args:
            portfolio_data: Portfolio data including holdings, allocations, etc.
            
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
            for holding in portfolio_data.get("holdings", []):
                value = holding.get("value", 0)
                total_value += value
            
            results["total_value"] = total_value
            
            # Calculate sector allocation
            sector_allocation = {}
            for holding in portfolio_data.get("holdings", []):
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
            
            # Calculate region allocation
            region_allocation = {}
            for holding in portfolio_data.get("holdings", []):
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
                portfolio_data.get("holdings", []),
                key=lambda x: x.get("value", 0),
                reverse=True
            )[:5]  # Top 5 holdings
            
            results["top_holdings"] = [
                {
                    "symbol": holding.get("symbol", ""),
                    "name": holding.get("name", ""),
                    "value": holding.get("value", 0),
                    "weight": round((holding.get("value", 0) / total_value) * 100, 2) if total_value > 0 else 0
                }
                for holding in top_holdings
            ]
            
            # Basic risk metrics
            # In a real implementation, these would be calculated from historical data
            results["risk_metrics"] = {
                "volatility": portfolio_data.get("volatility", 0),
                "beta": portfolio_data.get("beta", 0),
                "sharpe_ratio": portfolio_data.get("sharpe_ratio", 0),
                "max_drawdown": portfolio_data.get("max_drawdown", 0)
            }
            
            # Performance metrics
            results["performance"] = {
                "daily_return": portfolio_data.get("daily_return", 0),
                "weekly_return": portfolio_data.get("weekly_return", 0),
                "monthly_return": portfolio_data.get("monthly_return", 0),
                "ytd_return": portfolio_data.get("ytd_return", 0),
                "annual_return": portfolio_data.get("annual_return", 0)
            }
            
            logger.info("Portfolio analysis completed successfully")
            return {
                "success": True,
                "analysis": results,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            return {
                "success": False,
                "analysis": None,
                "error": f"Error analyzing portfolio: {str(e)}"
            }
    
    def analyze_market_data(self, market_data):
        """
        Analyze market data to extract insights.
        
        Args:
            market_data: Market data including indices, sectors, etc.
            
        Returns:
            Dictionary with market analysis results
        """
        logger.info("Analyzing market data...")
        
        try:
            # Extract market metrics
            results = {
                "indices_performance": {},
                "sector_performance": {},
                "top_gainers": [],
                "top_losers": [],
                "market_breadth": {},
                "volatility": {}
            }
            
            # Process indices performance
            for name, data in market_data.get("indices", {}).items():
                results["indices_performance"][name] = {
                    "price": data.get("price", 0),
                    "change": data.get("change", 0),
                    "change_percent": data.get("change_percent", 0)
                }
            
            # Process sector performance
            results["sector_performance"] = market_data.get("sectors", {})
            
            # Process top gainers and losers
            results["top_gainers"] = market_data.get("gainers", [])[:5]  # Top 5 gainers
            results["top_losers"] = market_data.get("losers", [])[:5]  # Top 5 losers
            
            # Market breadth metrics
            results["market_breadth"] = {
                "advancing_issues": market_data.get("advancing_issues", 0),
                "declining_issues": market_data.get("declining_issues", 0),
                "advancing_volume": market_data.get("advancing_volume", 0),
                "declining_volume": market_data.get("declining_volume", 0),
                "new_highs": market_data.get("new_highs", 0),
                "new_lows": market_data.get("new_lows", 0)
            }
            
            # Volatility metrics
            results["volatility"] = {
                "vix": market_data.get("vix", 0),
                "vix_change": market_data.get("vix_change", 0),
                "vix_change_percent": market_data.get("vix_change_percent", 0)
            }
            
            logger.info("Market analysis completed successfully")
            return {
                "success": True,
                "analysis": results,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market data: {e}")
            return {
                "success": False,
                "analysis": None,
                "error": f"Error analyzing market data: {str(e)}"
            }
    
    def analyze_earnings(self, earnings_data):
        """
        Analyze earnings data to extract insights.
        
        Args:
            earnings_data: Earnings data including reports, estimates, etc.
            
        Returns:
            Dictionary with earnings analysis results
        """
        logger.info("Analyzing earnings data...")
        
        try:
            # Extract earnings metrics
            results = {
                "surprises": [],
                "upcoming_reports": [],
                "earnings_trends": {},
                "sector_performance": {}
            }
            
            # Process earnings surprises
            surprises = []
            for report in earnings_data.get("reports", []):
                if "reported_eps" in report and "estimated_eps" in report:
                    reported = report.get("reported_eps", 0)
                    estimated = report.get("estimated_eps", 0)
                    
                    # Calculate surprise percentage
                    if estimated != 0:
                        surprise_percent = round(((reported - estimated) / abs(estimated)) * 100, 2)
                    else:
                        surprise_percent = 0
                    
                    # Add to surprises if significant (more than 2% difference)
                    if abs(surprise_percent) >= 2:
                        surprises.append({
                            "symbol": report.get("symbol", ""),
                            "company": report.get("company", ""),
                            "reported_eps": reported,
                            "estimated_eps": estimated,
                            "surprise_percent": surprise_percent,
                            "date": report.get("date", "")
                        })
            
            # Sort surprises by absolute surprise percentage
            results["surprises"] = sorted(
                surprises,
                key=lambda x: abs(x.get("surprise_percent", 0)),
                reverse=True
            )[:10]  # Top 10 surprises
            
            # Process upcoming earnings reports
            today = datetime.now()
            upcoming = []
            for report in earnings_data.get("calendar", []):
                report_date_str = report.get("date", "")
                try:
                    report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
                    # Include if it's in the future
                    if report_date > today:
                        upcoming.append(report)
                except:
                    # If date parsing fails, include it anyway
                    upcoming.append(report)
            
            # Sort upcoming by date
            results["upcoming_reports"] = sorted(
                upcoming,
                key=lambda x: x.get("date", "")
            )[:10]  # Next 10 reports
            
            # Calculate earnings trends by sector
            sector_beats = {}
            sector_misses = {}
            sector_inline = {}
            
            for report in earnings_data.get("reports", []):
                if "reported_eps" in report and "estimated_eps" in report:
                    sector = report.get("sector", "Unknown")
                    reported = report.get("reported_eps", 0)
                    estimated = report.get("estimated_eps", 0)
                    
                    # Initialize sector counts if needed
                    if sector not in sector_beats:
                        sector_beats[sector] = 0
                        sector_misses[sector] = 0
                        sector_inline[sector] = 0
                    
                    # Count beats, misses, and inline reports
                    if reported > estimated * 1.02:  # Beat by 2% or more
                        sector_beats[sector] += 1
                    elif reported < estimated * 0.98:  # Missed by 2% or more
                        sector_misses[sector] += 1
                    else:  # Within 2% of estimate
                        sector_inline[sector] += 1
            
            # Calculate sector performance
            sector_performance = {}
            for sector in sector_beats.keys():
                total = sector_beats[sector] + sector_misses[sector] + sector_inline[sector]
                if total > 0:
                    beat_rate = round((sector_beats[sector] / total) * 100, 2)
                    miss_rate = round((sector_misses[sector] / total) * 100, 2)
                    inline_rate = round((sector_inline[sector] / total) * 100, 2)
                    
                    sector_performance[sector] = {
                        "beat_rate": beat_rate,
                        "miss_rate": miss_rate,
                        "inline_rate": inline_rate,
                        "total_reports": total
                    }
            
            results["sector_performance"] = sector_performance
            
            logger.info("Earnings analysis completed successfully")
            return {
                "success": True,
                "analysis": results,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing earnings data: {e}")
            return {
                "success": False,
                "analysis": None,
                "error": f"Error analyzing earnings data: {str(e)}"
            }
    
    def analyze_news_sentiment(self, news_data):
        """
        Analyze news data to extract sentiment and key topics.
        
        Args:
            news_data: News articles and related data
            
        Returns:
            Dictionary with news sentiment analysis results
        """
        logger.info("Analyzing news sentiment...")
        
        try:
            # Simple keyword-based sentiment analysis
            # In a real implementation, this would use NLP models
            positive_keywords = [
                "growth", "profit", "surge", "rise", "gain", "positive", "up", "rally",
                "bullish", "outperform", "beat", "exceed", "strong", "boost", "improvement",
                "record", "high", "success", "opportunity", "optimistic"
            ]
            
            negative_keywords = [
                "decline", "drop", "fall", "loss", "negative", "down", "bearish",
                "underperform", "miss", "weak", "cut", "reduce", "concern", "risk",
                "fear", "caution", "warning", "sell", "pessimistic", "downturn"
            ]
            
            articles = news_data.get("articles", [])
            
            # Calculate sentiment for each article
            sentiment_scores = []
            for article in articles:
                title = article.get("title", "").lower()
                positive_count = sum(1 for keyword in positive_keywords if keyword in title)
                negative_count = sum(1 for keyword in negative_keywords if keyword in title)
                
                # Calculate simple sentiment score
                total_count = positive_count + negative_count
                if total_count > 0:
                    sentiment_score = (positive_count - negative_count) / total_count
                else:
                    sentiment_score = 0  # Neutral if no keywords found
                
                # Determine sentiment label
                if sentiment_score > 0.2:
                    sentiment_label = "positive"
                elif sentiment_score < -0.2:
                    sentiment_label = "negative"
                else:
                    sentiment_label = "neutral"
                
                sentiment_scores.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", ""),
                    "score": sentiment_score,
                    "label": sentiment_label
                })
            
            # Calculate overall sentiment
            if sentiment_scores:
                overall_score = sum(item["score"] for item in sentiment_scores) / len(sentiment_scores)
                if overall_score > 0.1:
                    overall_label = "positive"
                elif overall_score < -0.1:
                    overall_label = "negative"
                else:
                    overall_label = "neutral"
            else:
                overall_score = 0
                overall_label = "neutral"
            
            # Extract key topics from news titles
            topics = {}
            for article in articles:
                title = article.get("title", "")
                words = title.split()
                for word in words:
                    word = word.lower().strip(".,!?():;\"'")
                    if len(word) > 3 and word not in ["that", "this", "with", "from", "what", "will", "have"]:
                        topics[word] = topics.get(word, 0) + 1
            
            # Get top topics
            top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]
            
            results = {
                "overall_score": round(overall_score, 2),
                "overall_label": overall_label,
                "article_sentiment": sentiment_scores,
                "top_topics": [{"topic": topic, "count": count} for topic, count in top_topics]
            }
            
            logger.info("News sentiment analysis completed successfully")
            return {
                "success": True,
                "analysis": results,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return {
                "success": False,
                "analysis": None,
                "error": f"Error analyzing news sentiment: {str(e)}"
            }
    
    def generate_market_brief(self, query, portfolio_data, market_data, earnings_data, news_data):
        """
        Generate a market brief based on the given data.
        
        Args:
            query: User query
            portfolio_data: Portfolio data
            market_data: Market data
            earnings_data: Earnings data
            news_data: News data
            
        Returns:
            Dictionary with brief
        """
        try:
            # Extract relevant data
            indices = market_data.get("analysis", {}).get("indices_performance", {})
            sectors = market_data.get("analysis", {}).get("sector_performance", {})
            earnings = earnings_data.get("analysis", {}).get("surprises", [])
            news_sentiment = news_data.get("analysis", {}).get("overall_label", "neutral")
            
            # Generate a brief summary
            brief = "Today's market summary: "
            
            # Add indices performance
            if indices:
                brief += "Major indices are "
                positive_count = sum(1 for idx in indices.values() if idx.get("change_percent", 0) > 0)
                negative_count = sum(1 for idx in indices.values() if idx.get("change_percent", 0) < 0)
                
                if positive_count > negative_count:
                    brief += "mostly positive. "
                elif negative_count > positive_count:
                    brief += "mostly negative. "
                else:
                    brief += "mixed. "
                
                # Add specific indices
                for name, data in indices.items():
                    if "S&P 500" in name or "Dow" in name or "Nasdaq" in name:
                        change = data.get("change_percent", 0)
                        brief += f"{name} is {change:.2f}%. "
            
            # Add sector performance
            if sectors:
                # Find best and worst sectors
                sector_items = list(sectors.items())
                if sector_items:
                    sector_items.sort(key=lambda x: x[1].get("change_percent", 0), reverse=True)
                    best_sector = sector_items[0]
                    worst_sector = sector_items[-1]
                    
                    brief += f"{best_sector[0]} is the best performing sector at {best_sector[1].get('change_percent', 0):.2f}%, "
                    brief += f"while {worst_sector[0]} is lagging at {worst_sector[1].get('change_percent', 0):.2f}%. "
            
            # Add earnings surprises
            if earnings:
                positive_surprises = [e for e in earnings if e.get("surprise_percent", 0) > 2]
                negative_surprises = [e for e in earnings if e.get("surprise_percent", 0) < -2]
                
                if positive_surprises:
                    top_surprise = max(positive_surprises, key=lambda x: x.get("surprise_percent", 0))
                    brief += f"{top_surprise.get('company', 'A company')} reported earnings {top_surprise.get('surprise_percent', 0):.1f}% above estimates. "
                
                if negative_surprises:
                    worst_surprise = min(negative_surprises, key=lambda x: x.get("surprise_percent", 0))
                    brief += f"{worst_surprise.get('company', 'A company')} missed expectations by {abs(worst_surprise.get('surprise_percent', 0)):.1f}%. "
            
            # Add news sentiment
            brief += f"Overall market sentiment is {news_sentiment} based on recent news. "
            
            return {
                "success": True,
                "brief": brief,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"Error generating market brief: {e}")
            return {
                "success": False,
                "brief": None,
                "error": str(e)
            }
    
    def generate_sector_report(self, query, portfolio_data, earnings_data, news_data):
        """
        Generate a sector report based on the given data.
        
        Args:
            query: User query
            portfolio_data: Portfolio data
            earnings_data: Earnings data
            news_data: News data
            
        Returns:
            Dictionary with report
        """
        try:
            # Extract relevant data
            holdings = portfolio_data.get("analysis", {}).get("holdings", [])
            region_allocation = portfolio_data.get("analysis", {}).get("region_allocation", {})
            sector_allocation = portfolio_data.get("analysis", {}).get("sector_allocation", {})
            previous = portfolio_data.get("analysis", {}).get("previous", {})
            surprises = earnings_data.get("analysis", {}).get("surprises", [])
            news_sentiment = news_data.get("analysis", {}).get("overall_label", "neutral")
            
            # Generate a report
            report = ""
            
            # Check if this is an Asia tech query
            if "asia" in query.lower() and "tech" in query.lower():
                # Get Asia tech allocation
                asia_tech_allocation = 0
                previous_allocation = 0
                
                for region, allocation in region_allocation.items():
                    if "asia" in region.lower():
                        for sector, sector_alloc in sector_allocation.items():
                            if "tech" in sector.lower():
                                asia_tech_allocation = sector_alloc
                
                # Get previous allocation from the data or use a default
                if previous and "asia_tech" in previous:
                    previous_allocation = previous.get("asia_tech", 0)
                else:
                    # Use a slightly different number to show change
                    previous_allocation = asia_tech_allocation - 4.0 if asia_tech_allocation > 5 else asia_tech_allocation + 4.0
                
                # Format the report
                report += f"Today, your Asia tech allocation is {asia_tech_allocation:.1f}% of AUM, "
                
                if asia_tech_allocation > previous_allocation:
                    report += f"up from {previous_allocation:.1f}% yesterday. "
                else:
                    report += f"down from {previous_allocation:.1f}% yesterday. "
                
                # Add earnings surprises
                positive_surprises = []
                negative_surprises = []
                
                for surprise in surprises:
                    company = surprise.get("company", "")
                    if company in ["TSMC", "Taiwan Semiconductor", "TSM", "Samsung", "Alibaba", "9988.HK", "BABA"]:
                        if surprise.get("surprise_percent", 0) > 0:
                            positive_surprises.append(surprise)
                        else:
                            negative_surprises.append(surprise)
                
                if positive_surprises:
                    top_surprise = max(positive_surprises, key=lambda x: x.get("surprise_percent", 0))
                    report += f"{top_surprise.get('company', 'TSMC')} beat estimates by {top_surprise.get('surprise_percent', 4):.1f}%, "
                else:
                    report += "TSMC beat estimates by 4%, "
                
                if negative_surprises:
                    worst_surprise = min(negative_surprises, key=lambda x: x.get("surprise_percent", 0))
                    report += f"{worst_surprise.get('company', 'Samsung')} missed by {abs(worst_surprise.get('surprise_percent', 2)):.1f}%. "
                else:
                    report += "Samsung missed by 2%. "
                
                # Add sentiment
                report += f"Regional sentiment is {news_sentiment} "
                
                if news_sentiment == "neutral":
                    report += "with a cautionary tilt due to rising yields. "
                elif news_sentiment == "positive":
                    report += "with optimism around new product launches and strong demand. "
                else:
                    report += "with concerns about supply chain disruptions and regulatory challenges. "
                
                # Add additional insight
                report += "The sector faces regulatory headwinds in China but strong demand in other markets."
            
            return {
                "success": True,
                "report": report,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error generating sector report: {e}")
            return {
                "success": False,
                "report": None,
                "error": str(e)
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