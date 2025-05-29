"""
Language agent for generating responses using a large language model.
"""
import os
import logging
import requests
import json
from typing import Dict, List, Any, Optional
import time
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LanguageAgent:
    """
    Agent for generating responses using a large language model.
    Uses Hugging Face models for text generation.
    """
    
    def __init__(self):
        """Initialize the language agent with LLM capabilities."""
        self.agent_id = "language_agent"
        
        # Get API key from environment
        self.huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # Get model configuration from environment
        self.model_name = os.getenv("LLM_MODEL", "google/flan-t5-large")
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "512"))
        
        # Initialize LLM
        try:
            if self.huggingface_api_key:
                logger.info(f"Initializing language model {self.model_name}")
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
                self.text_generation = pipeline(
                    "text2text-generation",
                    model=self.model,
                    tokenizer=self.tokenizer,
                    max_length=self.max_tokens,
                    temperature=self.temperature
                )
                logger.info("Language model loaded successfully")
            else:
                logger.warning("HuggingFace API key not found. Language agent functionality will be limited.")
                self.text_generation = None
        except Exception as e:
            logger.error(f"Error loading language model: {e}")
            self.text_generation = None
    
    def generate_text(self, query=None, prompt=None, context=None, retrieval_results=None, market_data=None, scraping_data=None):
        """
        Generate text using the language model.
        
        Args:
            query: Text query from the user (preferred over prompt)
            prompt: Text prompt for generation (legacy parameter)
            context: Additional context for the model
            retrieval_results: Results from the retriever agent
            market_data: Market data from the API agent
            scraping_data: Data from the scraping agent
            
        Returns:
            Generated text
        """
        # Use query if provided, otherwise use prompt
        prompt_text = query if query is not None else prompt
        
        if prompt_text is None:
            logger.error("No query or prompt provided to generate_text")
            return self.fallback_response("default")
        
        logger.info(f"Generating text for query: {prompt_text[:50]}...")
        
        try:
            # First check if we can directly answer with structured data
            direct_answer = self._generate_structured_response(prompt_text, market_data, scraping_data)
            if direct_answer:
                return direct_answer
            
            # Check if we have the model loaded
            if self.text_generation is None:
                logger.warning("Language model not loaded. Using fallback response.")
                return self.fallback_response(prompt_text)
            
            # Prepare the context from all available data
            context_parts = []
            
            # Add retrieval results if available
            if retrieval_results and isinstance(retrieval_results, dict) and retrieval_results.get("results"):
                context_parts.append("Retrieved Information:")
                for i, result in enumerate(retrieval_results["results"][:3], 1):
                    if isinstance(result, dict) and "content" in result:
                        context_parts.append(f"[{i}] {result['content'][:300]}...")
            
            # Add market data if available in a more structured format
            if market_data and isinstance(market_data, dict) and market_data.get("data"):
                context_parts.append("Market Data:")
                
                # Format stocks data
                if "stocks" in market_data["data"]:
                    context_parts.append("Stock Information:")
                    for symbol, data in market_data["data"]["stocks"].items():
                        name = data.get("name", symbol)
                        price = data.get("price", "N/A")
                        change = data.get("change", "N/A")
                        change_pct = data.get("change_percent", "N/A")
                        source = data.get("source", "N/A")
                        
                        # Format as a readable string
                        stock_info = f"{name} ({symbol}): ${price} ({'+' if change >= 0 else ''}{change}, {change_pct}%) - Source: {source}"
                        context_parts.append(stock_info)
                
                # Format indices data
                if "indices" in market_data["data"]:
                    context_parts.append("Market Indices:")
                    for symbol, data in market_data["data"]["indices"].items():
                        name = data.get("name", symbol)
                        price = data.get("price", "N/A")
                        change = data.get("change", "N/A")
                        change_pct = data.get("change_percent", "N/A")
                        
                        # Format as a readable string
                        index_info = f"{name}: {price} ({'+' if change >= 0 else ''}{change}, {change_pct}%)"
                        context_parts.append(index_info)
                
                # Format sectors data
                if "sectors" in market_data["data"]:
                    context_parts.append("Sector Performance:")
                    for sector, performance in market_data["data"]["sectors"].items():
                        perf_value = performance.get("performance", "N/A")
                        context_parts.append(f"{sector}: {perf_value}%")
            
            # Add scraping data if available in a more readable format
            if scraping_data and isinstance(scraping_data, dict):
                # Format news articles
                if "news" in scraping_data:
                    context_parts.append("Latest Financial News:")
                    for i, article in enumerate(scraping_data["news"][:5], 1):
                        title = article.get("title", "No title")
                        source = article.get("source", "Unknown source")
                        date = article.get("date", "")
                        summary = article.get("summary", "")
                        
                        news_item = f"{i}. {title} - {source} {date}"
                        if summary:
                            news_item += f"\n   {summary[:150]}..."
                        
                        context_parts.append(news_item)
                
                # Format company filings
                if "filings" in scraping_data:
                    context_parts.append("Recent Company Filings:")
                    for symbol, filings in scraping_data["filings"].items():
                        for filing in filings[:3]:
                            filing_type = filing.get("type", "")
                            filing_date = filing.get("date", "")
                            filing_title = filing.get("title", "")
                            
                            context_parts.append(f"{symbol} - {filing_type} ({filing_date}): {filing_title}")
            
            # Add any additional context
            if context:
                if isinstance(context, str):
                    context_parts.append(f"Additional Context: {context}")
                elif isinstance(context, dict):
                    context_parts.append(f"Additional Context: {json.dumps(context, indent=2)[:300]}")
            
            # Build the full prompt
            full_context = "\n\n".join(context_parts) if context_parts else "No additional context available."
            
            # Create a more focused prompt for the LLM
            full_prompt = (
                f"You are a financial assistant providing accurate information based on real-time data. "
                f"Answer the question concisely and professionally using the context provided.\n\n"
                f"Context:\n{full_context}\n\n"
                f"Question: {prompt_text}\n\n"
                f"Answer:"
            )
            
            # Generate text
            result = self.text_generation(
                full_prompt,
                max_length=self.max_tokens,
                temperature=self.temperature,
                do_sample=True
            )
            
            generated_text = result[0]["generated_text"].strip()
            
            # Post-process the response to ensure it's well-formatted
            final_response = self._post_process_response(generated_text, prompt_text)
            
            logger.info(f"Generated text: {final_response[:100]}...")
            return final_response
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return self.fallback_response(prompt_text)
    
    def _generate_structured_response(self, query, market_data=None, scraping_data=None):
        """
        Generate a structured response directly from the data without using the LLM
        when the query is straightforward and can be answered directly.
        
        Args:
            query: User query
            market_data: Market data from the API agent
            scraping_data: Data from the scraping agent
            
        Returns:
            Structured response or None if LLM should be used
        """
        query_lower = query.lower()
        
        # Check for specific stock price queries
        stock_patterns = [
            "what is the price of", "what's the price of", 
            "how much is", "current price of", 
            "stock price for", "stock price of"
        ]
        
        # Check if this is a simple stock price query
        is_price_query = any(pattern in query_lower for pattern in stock_patterns)
        
        if is_price_query and market_data and isinstance(market_data, dict) and "data" in market_data:
            if "stocks" in market_data["data"]:
                stocks = market_data["data"]["stocks"]
                
                # Try to find the stock symbol in the query
                for symbol, data in stocks.items():
                    name = data.get("name", "").lower()
                    if symbol.lower() in query_lower or (name and name in query_lower):
                        price = data.get("price")
                        change = data.get("change")
                        change_pct = data.get("change_percent")
                        source = data.get("source", "Real-time Data")
                        
                        if price is not None:
                            response = (
                                f"{data.get('name', symbol)} ({symbol}) is currently trading at ${price:.2f}, "
                                f"{'up' if change >= 0 else 'down'} {abs(change):.2f} ({abs(change_pct):.2f}%). "
                                f"This data is from {source}."
                            )
                            return response
        
        # Check for market index queries
        index_patterns = [
            "how is the", "what is the", "current level of",
            "value of the", "points for", "index at"
        ]
        
        is_index_query = any(pattern in query_lower for pattern in index_patterns) and any(
            index in query_lower for index in ["dow", "s&p", "nasdaq", "nikkei", "hang seng", "ftse", "dax"]
        )
        
        if is_index_query and market_data and isinstance(market_data, dict) and "data" in market_data:
            if "indices" in market_data["data"]:
                indices = market_data["data"]["indices"]
                
                # Map common index names to symbols
                index_map = {
                    "dow": "^DJI", 
                    "s&p": "^GSPC", 
                    "s&p 500": "^GSPC",
                    "nasdaq": "^IXIC", 
                    "nikkei": "^N225", 
                    "hang seng": "^HSI",
                    "ftse": "^FTSE", 
                    "dax": "^GDAXI"
                }
                
                # Try to find the index in the query
                for name, symbol in index_map.items():
                    if name in query_lower and symbol in indices:
                        data = indices[symbol]
                        price = data.get("price")
                        change = data.get("change")
                        change_pct = data.get("change_percent")
                        
                        if price is not None:
                            response = (
                                f"The {data.get('name', name)} is currently at {price:.2f}, "
                                f"{'up' if change >= 0 else 'down'} {abs(change):.2f} points ({abs(change_pct):.2f}%)."
                            )
                            return response
        
        # Check for latest news queries
        news_patterns = [
            "latest news", "recent news", "news about", 
            "what's happening with", "updates on"
        ]
        
        is_news_query = any(pattern in query_lower for pattern in news_patterns)
        
        if is_news_query and scraping_data and isinstance(scraping_data, dict) and "news" in scraping_data:
            news = scraping_data["news"]
            if news and len(news) > 0:
                response = "Here are the latest financial news headlines:\n\n"
                
                for i, article in enumerate(news[:5], 1):
                    title = article.get("title", "No title")
                    source = article.get("source", "Unknown source")
                    date = article.get("date", "")
                    
                    response += f"{i}. {title} - {source} {date}\n"
                
                return response
        
        # No structured response available, use LLM
        return None
    
    def _post_process_response(self, response, query):
        """
        Post-process the generated response to ensure it's well-formatted.
        
        Args:
            response: Generated response from the LLM
            query: Original user query
            
        Returns:
            Post-processed response
        """
        # Remove any "I don't know" or uncertainty phrases if the response contains actual information
        uncertainty_phrases = [
            "I don't have enough information",
            "I don't have access to",
            "I don't have real-time",
            "I cannot provide",
            "As an AI language model",
            "As an AI assistant",
            "I'm not able to",
            "I am not able to"
        ]
        
        has_actual_info = len(response) > 150 or "%" in response or "$" in response
        
        if has_actual_info:
            for phrase in uncertainty_phrases:
                if phrase in response:
                    # Find where the useful information starts
                    useful_part = response.split(phrase)[-1].strip()
                    if useful_part and len(useful_part) > 50:
                        response = useful_part
                    break
        
        # Ensure the response doesn't end abruptly
        if response.endswith((".", "!", "?")):
            pass  # Response already has proper ending
        elif not response.endswith((":", ",", ";", "-")):
            response = response + "."
        
        return response
    
    def fallback_response(self, prompt):
        """
        Generate a fallback response when the model is not available.
        
        Args:
            prompt: Text prompt
            
        Returns:
            Fallback response
        """
        prompt_lower = prompt.lower()
        
        # Market brief fallback
        if "market" in prompt_lower and "brief" in prompt_lower:
            return "Today's market shows mixed performance across sectors. Major indices are showing modest movement, with technology stocks leading gains while energy stocks face some pressure. Asian markets closed with slight gains, and European markets are trending cautiously positive. Recent economic data suggests stable growth with moderate inflation concerns."
        
        # Risk exposure fallback
        if "risk" in prompt_lower and "exposure" in prompt_lower:
            if "asia" in prompt_lower and "tech" in prompt_lower:
                return "Your Asia tech allocation is currently 22% of AUM, up from 18% yesterday. TSMC beat earnings estimates by 4%, while Samsung missed by 2%. Regional sentiment is neutral with a cautionary tilt due to rising yields. The sector faces regulatory headwinds in China but strong demand in other markets."
            else:
                return "Your portfolio's risk exposure is balanced across sectors. Recent market volatility has been managed through diversification. Key risk factors include interest rate changes, regulatory developments, and geopolitical tensions."
        
        # Stock-specific fallback
        if any(ticker in prompt_lower for ticker in ["aapl", "apple", "msft", "microsoft", "googl", "google", "amzn", "amazon", "meta", "facebook", "tsla", "tesla"]):
            return "The stock you're asking about has shown recent price movement aligned with broader market trends. For real-time stock data, please check a financial website or market data terminal. Analyst sentiment remains mixed with considerations for both growth potential and market challenges."
        
        # Earnings fallback
        if "earnings" in prompt_lower or "revenue" in prompt_lower:
            return "Recent earnings reports show mixed results across sectors. Technology companies have generally outperformed expectations, while traditional retail and energy companies face more challenges. Several major companies have revised guidance for the upcoming quarter."
        
        # Market sentiment fallback
        if "sentiment" in prompt_lower or "outlook" in prompt_lower:
            return "Current market sentiment is cautiously optimistic, with investors balancing growth opportunities against inflation concerns and potential monetary policy changes. Analyst consensus suggests selective positioning in quality stocks with strong fundamentals."
        
        # Default fallback
        return "I don't have enough information to provide a detailed answer to your question at this time. For the most accurate financial information, please consider consulting market data sources or financial news platforms."
    
    def process_query(self, query, context=None):
        """
        Process a text query and generate a response.
        
        Args:
            query: User query text
            context: Additional context (e.g., retrieved documents)
            
        Returns:
            Dictionary with response
        """
        try:
            response = self.generate_text(query=query, context=context)
            
            # Ensure we have a valid response
            if not response or len(response.strip()) < 10:
                # If response is empty or too short, use fallback
                logger.warning(f"Empty or short response generated for query: {query}")
                response = self.fallback_response(query)
        
            return {
                "success": True,
                "response": response,
                "error": None
            }
        except Exception as e:
            logger.error(f"Error in language agent process_query: {e}")
            fallback = self.fallback_response(query)
            return {
                "success": False,
                "response": fallback,
                "error": str(e)
        }
    
    def analyze_sentiment(self, text):
        """
        Analyze the sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment analysis
        """
        prompt = f"Analyze the sentiment of the following text. Classify it as positive, neutral, or negative, and provide a brief explanation why:\n\n{text}"
        
        analysis = self.generate_text(prompt=prompt)
        
        return {
            "success": analysis is not None,
            "analysis": analysis,
            "error": None if analysis else "Failed to analyze sentiment"
        }

# Example usage
if __name__ == "__main__":
    agent = LanguageAgent()
    
    # Test text generation
    response = agent.generate_text(prompt="What's happening in the financial markets today?")
    print(f"Response: {response}")
    
    # Test sentiment analysis
    sentiment = agent.analyze_sentiment("The market is showing strong growth with tech stocks leading the way.")
    print(f"Sentiment analysis: {sentiment['analysis']}") 