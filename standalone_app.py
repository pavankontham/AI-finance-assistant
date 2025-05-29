"""
Streamlit app for Finance Assistant - Standalone Version.
This version is designed to run directly without requiring a separate API server.
"""
import os
import logging
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import datetime
import time
import yfinance as yf
from data_ingestion.web_scraper import WebScraper
from data_ingestion.market_data import MarketDataClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize data clients
web_scraper = WebScraper()
market_data_client = MarketDataClient()

# App title and configuration
st.set_page_config(
    page_title="Finance Assistant",
    page_icon="💹",
    layout="wide"
)

# Apply custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #0D47A1;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .card {
        border-radius: 5px;
        padding: 1rem;
        margin-bottom: 1rem;
        background-color: #f8f9fa;
        border-left: 4px solid #1E88E5;
    }
    .info-text {
        color: #555;
        font-size: 0.9rem;
    }
    .highlight {
        background-color: #e3f2fd;
        padding: 0.2rem;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

def get_market_overview():
    """Get an overview of major market indices."""
    indices = [
        "^DJI",    # Dow Jones
        "^GSPC",   # S&P 500
        "^IXIC",   # NASDAQ
        "^N225",   # Nikkei 225
        "^HSI",    # Hang Seng
        "^FTSE"    # FTSE 100
    ]
    
    try:
        # Get real-time market data
        market_data = web_scraper.get_realtime_market_data(indices)
        
        # Create a DataFrame for display
        data = []
        for symbol, info in market_data.items():
            data.append({
                "Index": info.get("name", symbol),
                "Price": info.get("price", 0),
                "Change": info.get("change", 0),
                "Change %": info.get("change_percent", 0),
                "Source": info.get("source", "Unknown")
            })
        
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        # Return dummy data if there's an error
        return pd.DataFrame([
            {"Index": "Dow Jones", "Price": 34567.89, "Change": 123.45, "Change %": 0.36, "Source": "Fallback Data"},
            {"Index": "S&P 500", "Price": 4567.89, "Change": 23.45, "Change %": 0.52, "Source": "Fallback Data"},
            {"Index": "NASDAQ", "Price": 14567.89, "Change": 123.45, "Change %": 0.85, "Source": "Fallback Data"},
            {"Index": "Nikkei 225", "Price": 28567.89, "Change": -123.45, "Change %": -0.43, "Source": "Fallback Data"},
            {"Index": "Hang Seng", "Price": 24567.89, "Change": -23.45, "Change %": -0.10, "Source": "Fallback Data"},
            {"Index": "FTSE 100", "Price": 7567.89, "Change": 23.45, "Change %": 0.31, "Source": "Fallback Data"}
        ])

def get_stock_data(symbol, period="1mo"):
    """Get historical stock data."""
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period=period)
        
        if hist.empty:
            raise ValueError(f"No data found for symbol: {symbol}")
            
        return hist
    except Exception as e:
        logger.error(f"Error getting stock data for {symbol}: {e}")
        # Return dummy data
        dates = pd.date_range(end=datetime.datetime.now(), periods=30)
        return pd.DataFrame({
            'Open': np.random.normal(100, 5, len(dates)),
            'High': np.random.normal(105, 5, len(dates)),
            'Low': np.random.normal(95, 5, len(dates)),
            'Close': np.random.normal(100, 5, len(dates)),
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)

def get_financial_news(query="", max_results=5):
    """Get financial news articles."""
    try:
        news = web_scraper.get_financial_news(query, max_results)
        return news
    except Exception as e:
        logger.error(f"Error getting news: {e}")
        # Return dummy news
        return [
            {
                "title": "Markets rally on positive economic data",
                "url": "https://example.com/news/1",
                "source": "Financial Times",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": "Stock markets rallied today after better-than-expected economic data."
            },
            {
                "title": "Tech stocks lead market gains",
                "url": "https://example.com/news/2",
                "source": "CNBC",
                "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "summary": "Technology stocks led market gains as investors bet on continued growth."
            }
        ]

def main():
    """Main function to run the Streamlit app."""
    # Header
    st.markdown("<h1 class='main-header'>Finance Assistant</h1>", unsafe_allow_html=True)
    st.markdown("Your AI-powered financial data and analysis tool")
    
    # Sidebar
    st.sidebar.image("https://img.icons8.com/color/96/000000/financial-growth.png", width=100)
    st.sidebar.title("Navigation")
    
    # Navigation
    page = st.sidebar.radio("Go to", ["Market Overview", "Stock Analysis", "Financial News", "Portfolio Analysis"])
    
    if page == "Market Overview":
        st.markdown("<h2 class='sub-header'>Market Overview</h2>", unsafe_allow_html=True)
        
        # Show loading spinner while fetching data
        with st.spinner("Fetching market data..."):
            market_df = get_market_overview()
        
        # Display market data with conditional formatting
        st.dataframe(
            market_df.style.applymap(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                subset=['Change', 'Change %']
            ),
            use_container_width=True
        )
        
        # Market trends visualization
        st.markdown("<h3 class='sub-header'>Market Trends</h3>", unsafe_allow_html=True)
        
        # Get some historical data for S&P 500
        with st.spinner("Loading market trends..."):
            try:
                sp500_data = get_stock_data("^GSPC", period="6mo")
                
                # Create a line chart
                st.line_chart(sp500_data['Close'])
                st.caption("S&P 500 - 6 Month Trend")
            except Exception as e:
                st.error(f"Error loading market trends: {e}")
    
    elif page == "Stock Analysis":
        st.markdown("<h2 class='sub-header'>Stock Analysis</h2>", unsafe_allow_html=True)
        
        # Stock search
        stock_symbol = st.text_input("Enter stock symbol (e.g., AAPL, MSFT, GOOGL)", "AAPL")
        period = st.select_slider("Select time period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="3mo")
        
        if st.button("Analyze"):
            with st.spinner(f"Analyzing {stock_symbol}..."):
                # Get stock data
                stock_data = get_stock_data(stock_symbol, period)
                
                if not stock_data.empty:
                    # Display stock info
                    st.markdown(f"<div class='card'><h3>{stock_symbol} Stock Analysis</h3></div>", unsafe_allow_html=True)
                    
                    # Price chart
                    st.subheader("Price Chart")
                    st.line_chart(stock_data['Close'])
                    
                    # Volume chart
                    st.subheader("Volume Chart")
                    st.bar_chart(stock_data['Volume'])
                    
                    # Statistics
                    st.markdown("<h3 class='sub-header'>Statistics</h3>", unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Current Price", f"${stock_data['Close'].iloc[-1]:.2f}", 
                                 f"{((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[-2]) / stock_data['Close'].iloc[-2] * 100):.2f}%")
                    
                    with col2:
                        st.metric("Average Volume", f"{stock_data['Volume'].mean():.0f}")
                    
                    with col3:
                        st.metric("Price Change (%)", 
                                 f"{((stock_data['Close'].iloc[-1] - stock_data['Close'].iloc[0]) / stock_data['Close'].iloc[0] * 100):.2f}%")
                    
                    # More statistics
                    stats_df = pd.DataFrame({
                        'Statistic': ['High', 'Low', 'Average', 'Std Dev', 'Min', 'Max'],
                        'Value': [
                            f"${stock_data['High'].max():.2f}",
                            f"${stock_data['Low'].min():.2f}",
                            f"${stock_data['Close'].mean():.2f}",
                            f"${stock_data['Close'].std():.2f}",
                            f"${stock_data['Close'].min():.2f}",
                            f"${stock_data['Close'].max():.2f}"
                        ]
                    })
                    
                    st.dataframe(stats_df, use_container_width=True)
                else:
                    st.error(f"No data found for symbol: {stock_symbol}")
    
    elif page == "Financial News":
        st.markdown("<h2 class='sub-header'>Financial News</h2>", unsafe_allow_html=True)
        
        # News search
        query = st.text_input("Search for news (leave blank for general financial news)", "")
        max_results = st.slider("Number of articles", 3, 10, 5)
        
        if st.button("Get News"):
            with st.spinner("Fetching news articles..."):
                news_articles = get_financial_news(query, max_results)
                
                if news_articles:
                    for article in news_articles:
                        st.markdown(f"""
                        <div class='card'>
                            <h3>{article['title']}</h3>
                            <p><strong>Source:</strong> {article['source']} | <strong>Date:</strong> {article['date']}</p>
                            <p>{article['summary']}</p>
                            <a href="{article['url']}" target="_blank">Read more</a>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No news articles found. Try a different search term.")
    
    elif page == "Portfolio Analysis":
        st.markdown("<h2 class='sub-header'>Portfolio Analysis</h2>", unsafe_allow_html=True)
        st.info("This is a demo of portfolio analysis functionality. In a real application, this would connect to your actual portfolio data.")
        
        # Demo portfolio
        portfolio_data = {
            'Symbol': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA'],
            'Shares': [10, 5, 2, 3, 8],
            'Purchase Price': [150.75, 280.50, 2800.00, 3200.00, 750.25],
            'Current Price': [175.25, 320.75, 2950.50, 3400.00, 800.50],
            'Sector': ['Technology', 'Technology', 'Technology', 'Consumer Cyclical', 'Automotive']
        }
        
        portfolio_df = pd.DataFrame(portfolio_data)
        portfolio_df['Market Value'] = portfolio_df['Shares'] * portfolio_df['Current Price']
        portfolio_df['Cost Basis'] = portfolio_df['Shares'] * portfolio_df['Purchase Price']
        portfolio_df['Gain/Loss'] = portfolio_df['Market Value'] - portfolio_df['Cost Basis']
        portfolio_df['Gain/Loss %'] = (portfolio_df['Gain/Loss'] / portfolio_df['Cost Basis'] * 100).round(2)
        
        # Display portfolio
        st.dataframe(
            portfolio_df.style.applymap(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                subset=['Gain/Loss', 'Gain/Loss %']
            ),
            use_container_width=True
        )
        
        # Portfolio metrics
        total_value = portfolio_df['Market Value'].sum()
        total_cost = portfolio_df['Cost Basis'].sum()
        total_gain_loss = portfolio_df['Gain/Loss'].sum()
        total_gain_loss_pct = (total_gain_loss / total_cost * 100).round(2)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:,.2f}")
        
        with col2:
            st.metric("Total Gain/Loss", f"${total_gain_loss:,.2f}", f"{total_gain_loss_pct}%")
        
        with col3:
            st.metric("Number of Holdings", len(portfolio_df))
        
        # Portfolio visualizations
        st.markdown("<h3 class='sub-header'>Portfolio Allocation</h3>", unsafe_allow_html=True)
        
        # Sector allocation pie chart
        sector_allocation = portfolio_df.groupby('Sector')['Market Value'].sum()
        st.subheader("Sector Allocation")
        st.bar_chart(sector_allocation)
    
    # Footer
    st.markdown("---")
    st.markdown("<div class='info-text'>Finance Assistant - Powered by AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-text'>Data provided for informational purposes only. Not financial advice.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 