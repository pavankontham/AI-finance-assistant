"""
Voice-Based Finance Assistant - Streamlit App
This app provides a voice interface for financial data and analysis.
"""
import os
import logging
import streamlit as st
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import datetime
import time
import json
import base64
from io import BytesIO
import gtts
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
import requests

# Import our custom VoiceAgent
from agents.voice_agent import VoiceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API keys
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")

# App title and configuration
st.set_page_config(
    page_title="Voice Finance Assistant",
    page_icon="🎙️",
    layout="wide"
)

# Initialize voice agent
voice_agent = VoiceAgent()

# Initialize API clients
alpha_ts = TimeSeries(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')
alpha_fd = FundamentalData(key=ALPHA_VANTAGE_API_KEY, output_format='pandas')

# Initialize session state
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = None
if 'voice_response' not in st.session_state:
    st.session_state.voice_response = None
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'last_response' not in st.session_state:
    st.session_state.last_response = ""
if 'market_data' not in st.session_state:
    st.session_state.market_data = None
if 'portfolio_data' not in st.session_state:
    # Initialize with some sample portfolio holdings that we'll get real data for
    st.session_state.portfolio_data = pd.DataFrame([
        {"Symbol": "AAPL", "Name": "Apple Inc.", "Shares": 500, "Sector": "Technology", "Region": "North America"},
        {"Symbol": "MSFT", "Name": "Microsoft Corp.", "Shares": 300, "Sector": "Technology", "Region": "North America"},
        {"Symbol": "TSM", "Name": "Taiwan Semiconductor", "Shares": 400, "Sector": "Technology", "Region": "Asia"},
        {"Symbol": "9988.HK", "Name": "Alibaba Group", "Shares": 1500, "Sector": "Consumer Cyclical", "Region": "Asia"},
        {"Symbol": "005930.KS", "Name": "Samsung Electronics", "Shares": 250, "Sector": "Technology", "Region": "Asia"}
    ])

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
    .voice-button {
        background-color: #1E88E5;
        color: white;
        border-radius: 50%;
        width: 100px;
        height: 100px;
        font-size: 1.5rem;
        margin: 1rem auto;
        display: block;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e8eaf6;
        border-left: 4px solid #3f51b5;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

def text_to_speech(text):
    """Convert text to speech and return audio bytes."""
    return voice_agent.text_to_speech(text)

def process_audio_file(audio_file):
    """Process an uploaded audio file and convert to text."""
    return voice_agent.speech_to_text(audio_file)

def get_market_data():
    """Get real-time market data for major indices."""
    try:
        # List of major indices
        indices = {
            "^DJI": "Dow Jones",
            "^GSPC": "S&P 500",
            "^IXIC": "NASDAQ",
            "^N225": "Nikkei 225",
            "^HSI": "Hang Seng",
            "^FTSE": "FTSE 100"
        }
        
        # Get data for each index
        data = []
        for symbol, name in indices.items():
            index = yf.Ticker(symbol)
            info = index.info
            history = index.history(period="2d")
            
            if not history.empty:
                current_price = history['Close'].iloc[-1]
                prev_price = history['Close'].iloc[-2] if len(history) > 1 else current_price
                change = current_price - prev_price
                change_pct = (change / prev_price) * 100 if prev_price != 0 else 0
                
                data.append({
                    "Index": name,
                    "Price": round(current_price, 2),
                    "Change": round(change, 2),
                    "Change %": round(change_pct, 2)
                })
        
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error fetching market data: {e}")
        # Return minimal data if API fails
        return pd.DataFrame([
            {"Index": "Data temporarily unavailable", "Price": 0, "Change": 0, "Change %": 0}
        ])

def get_portfolio_data():
    """Get real-time data for portfolio holdings."""
    try:
        # Get the base portfolio with share counts
        portfolio = st.session_state.portfolio_data.copy()
        
        # Get current prices and calculate values
        for i, row in portfolio.iterrows():
            symbol = row['Symbol']
            shares = row['Shares']
            
            try:
                stock = yf.Ticker(symbol)
                current_price = stock.info.get('regularMarketPrice', 0)
                if current_price is None:
                    current_price = stock.history(period="1d")['Close'].iloc[-1]
                
                portfolio.at[i, 'Price'] = current_price
                portfolio.at[i, 'Value'] = current_price * shares
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
                portfolio.at[i, 'Price'] = 0
                portfolio.at[i, 'Value'] = 0
        
        return portfolio
    except Exception as e:
        logger.error(f"Error processing portfolio data: {e}")
        return st.session_state.portfolio_data

def get_earnings_surprises(days=30):
    """Get real earnings surprises data."""
    try:
        # Use Alpha Vantage for earnings data
        # For demo purposes, we'll use a limited set of stocks
        symbols = ["AAPL", "MSFT", "GOOGL", "META", "AMZN"]
        earnings_data = []
        
        for symbol in symbols:
            try:
                # Get earnings data
                url = f"https://www.alphavantage.co/query?function=EARNINGS&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
                r = requests.get(url)
                data = r.json()
                
                if 'quarterlyEarnings' in data and data['quarterlyEarnings']:
                    # Get the most recent quarter
                    latest = data['quarterlyEarnings'][0]
                    
                    # Parse the data
                    reported_date = latest.get('reportedDate', '')
                    reported_eps = float(latest.get('reportedEPS', 0))
                    estimated_eps = float(latest.get('estimatedEPS', 0))
                    
                    # Calculate surprise percentage
                    if estimated_eps != 0:
                        surprise_pct = ((reported_eps - estimated_eps) / abs(estimated_eps)) * 100
                    else:
                        surprise_pct = 0
                    
                    # Get company info
                    stock = yf.Ticker(symbol)
                    company_name = stock.info.get('shortName', symbol)
                    sector = stock.info.get('sector', 'Unknown')
                    
                    # Add to our data
                    earnings_data.append({
                        "Symbol": symbol,
                        "Company": company_name,
                        "Expected EPS": estimated_eps,
                        "Actual EPS": reported_eps,
                        "Surprise %": round(surprise_pct, 2),
                        "Date": reported_date,
                        "Sector": sector
                    })
            except Exception as e:
                logger.error(f"Error fetching earnings for {symbol}: {e}")
        
        return pd.DataFrame(earnings_data)
    except Exception as e:
        logger.error(f"Error fetching earnings data: {e}")
        return pd.DataFrame()

def process_query(query):
    """Process a text query and return a response with real data."""
    try:
        # Get real-time portfolio data
        portfolio_data = get_portfolio_data()
        
        # Calculate Asia tech exposure
        asia_tech = portfolio_data[(portfolio_data['Region'] == 'Asia') & 
                                   (portfolio_data['Sector'] == 'Technology')]
        asia_tech_value = asia_tech['Value'].sum()
        total_value = portfolio_data['Value'].sum()
        asia_tech_pct = (asia_tech_value / total_value * 100) if total_value > 0 else 0
        
        # Get earnings data
        earnings_data = get_earnings_surprises()
        
        # Get market data
        market_data = get_market_data()
        
        # Process the query based on real data
        if "asia" in query.lower() and "tech" in query.lower():
            # Format the top holdings for the response
            top_holdings = ""
            for _, row in asia_tech.sort_values('Value', ascending=False).head(3).iterrows():
                top_holdings += f"{row['Name']} ({round(row['Value']/total_value*100, 1)}%), "
            
            return f"Your Asia tech allocation is currently {asia_tech_pct:.1f}% of your total portfolio value. Top holdings in this segment include {top_holdings[:-2]}."
        
        elif "earnings" in query.lower() or "surprises" in query.lower():
            if not earnings_data.empty:
                # Calculate percentage of companies that beat expectations
                beat_count = len(earnings_data[earnings_data['Surprise %'] > 0])
                total_count = len(earnings_data)
                beat_pct = (beat_count / total_count * 100) if total_count > 0 else 0
                
                # Get top positive and negative surprises
                top_positive = earnings_data.sort_values('Surprise %', ascending=False).iloc[0]
                top_negative = earnings_data.sort_values('Surprise %').iloc[0]
                
                return f"{beat_pct:.0f}% of companies beat earnings expectations. {top_positive['Company']} beat estimates by {top_positive['Surprise %']:.1f}%, while {top_negative['Company']} missed estimates by {abs(top_negative['Surprise %']):.1f}%."
            else:
                return "I couldn't retrieve the latest earnings data. Please try again later."
        
        elif "market" in query.lower() or "overview" in query.lower():
            if not market_data.empty and market_data['Index'].iloc[0] != "Data temporarily unavailable":
                # Calculate overall market sentiment
                positive_indices = len(market_data[market_data['Change %'] > 0])
                total_indices = len(market_data)
                
                sentiment = "bullish" if positive_indices / total_indices > 0.6 else \
                           "bearish" if positive_indices / total_indices < 0.4 else "mixed"
                
                # Format the response with real data
                sp500 = market_data[market_data['Index'] == 'S&P 500'].iloc[0]
                dow = market_data[market_data['Index'] == 'Dow Jones'].iloc[0]
                nasdaq = market_data[market_data['Index'] == 'NASDAQ'].iloc[0]
                
                return f"Overall market sentiment today is {sentiment}. The S&P 500 is {['down', 'up'][sp500['Change'] > 0]} {abs(sp500['Change %']):.1f}%, the Dow Jones is {['down', 'up'][dow['Change'] > 0]} {abs(dow['Change %']):.1f}%, and the NASDAQ is {['down', 'up'][nasdaq['Change'] > 0]} {abs(nasdaq['Change %']):.1f}%."
            else:
                return "I couldn't retrieve the latest market data. Please try again later."
        else:
            return f"I understand you're asking about: {query}\n\nTo get specific financial information, try asking about market overview, portfolio exposure (especially in regions like Asia or sectors like Technology), or recent earnings surprises."
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        return f"I'm having trouble processing your query due to a data access issue. Please try again later or ask a different question."

def main():
    """Main function to run the Streamlit app."""
    # Header
    st.markdown("<h1 class='main-header'>Voice Finance Assistant</h1>", unsafe_allow_html=True)
    st.markdown("Your AI-powered financial data and analysis tool with voice interface")
    
    # Sidebar
    st.sidebar.image("https://img.icons8.com/color/96/000000/voice-recognition.png", width=100)
    st.sidebar.title("Navigation")
    
    # Navigation
    page = st.sidebar.radio("Go to", ["Voice Assistant", "Market Overview", "Portfolio Analysis", "Earnings Surprises"])
    
    if page == "Voice Assistant":
        st.markdown("<h2 class='sub-header'>Voice Assistant</h2>", unsafe_allow_html=True)
        
        # Example queries
        st.markdown("### Example Queries:")
        st.markdown("- What's our risk exposure in Asia tech stocks today?")
        st.markdown("- Highlight any earnings surprises in the technology sector.")
        st.markdown("- Give me a summary of today's market performance.")
        
        # Voice input
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown("### Speak your query:")
            
            # Record audio button
            if st.button("🎙️ Hold to Record", key="record"):
                with st.spinner("Listening..."):
                    # In a real implementation, this would record audio
                    # For this demo, we'll simulate a voice query
                    st.session_state.last_query = "What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?"
                    
                    # Process the query
                    response = process_query(st.session_state.last_query)
                    st.session_state.last_response = response
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({"role": "user", "content": st.session_state.last_query})
                    st.session_state.conversation_history.append({"role": "assistant", "content": response})
                    
                    # Generate audio response
                    st.session_state.audio_bytes = text_to_speech(response)
            
            # Audio file upload option
            st.markdown("### Or upload an audio file:")
            uploaded_file = st.file_uploader("Choose an audio file", type=["wav", "mp3", "ogg"])
            
            if uploaded_file is not None:
                with st.spinner("Processing audio file..."):
                    # Save the uploaded file
                    audio_bytes = uploaded_file.read()
                    
                    # Process the audio file
                    query = process_audio_file(audio_bytes)
                    
                    if query:
                        st.session_state.last_query = query
                        st.success(f"Transcribed: {query}")
                        
                        # Process the query
                        response = process_query(query)
                        st.session_state.last_response = response
                        
                        # Add to conversation history
                        st.session_state.conversation_history.append({"role": "user", "content": query})
                        st.session_state.conversation_history.append({"role": "assistant", "content": response})
                        
                        # Generate audio response
                        st.session_state.audio_bytes = text_to_speech(response)
                    else:
                        st.error("Could not process the audio file. Please try again with a different file.")
        
        with col2:
            # Text input as an alternative
            text_query = st.text_input("Or type your query:", key="text_query")
            if st.button("Submit"):
                if text_query:
                    with st.spinner("Processing..."):
                        st.session_state.last_query = text_query
                        
                        # Process the query
                        response = process_query(text_query)
                        st.session_state.last_response = response
                        
                        # Add to conversation history
                        st.session_state.conversation_history.append({"role": "user", "content": text_query})
                        st.session_state.conversation_history.append({"role": "assistant", "content": response})
                        
                        # Generate audio response
                        st.session_state.audio_bytes = text_to_speech(response)
        
        # Display the audio player if audio is available
        if st.session_state.audio_bytes:
            st.audio(st.session_state.audio_bytes, format="audio/mp3")
        
        # Display conversation history
        st.markdown("### Conversation History:")
        for message in st.session_state.conversation_history:
            if message["role"] == "user":
                st.markdown(f"<div class='chat-message user-message'><strong>You:</strong> {message['content']}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-message assistant-message'><strong>Assistant:</strong> {message['content']}</div>", unsafe_allow_html=True)
    
    elif page == "Market Overview":
        st.markdown("<h2 class='sub-header'>Market Overview</h2>", unsafe_allow_html=True)
        
        # Show loading spinner while fetching data
        with st.spinner("Fetching real-time market data..."):
            market_df = get_market_data()
            st.session_state.market_data = market_df
        
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
        
        # Create a line chart with real data
        try:
            # Get S&P 500 data for the past 6 months
            sp500 = yf.Ticker("^GSPC")
            end_date = datetime.datetime.now()
            start_date = end_date - datetime.timedelta(days=180)
            hist = sp500.history(start=start_date, end=end_date)
            
            if not hist.empty:
                chart_data = hist[['Close']].rename(columns={'Close': 'Value'})
                st.line_chart(chart_data)
                st.caption("S&P 500 - 6 Month Trend")
            else:
                st.error("Could not retrieve historical market data.")
        except Exception as e:
            logger.error(f"Error fetching market trends: {e}")
            st.error("Could not retrieve historical market data.")
    
    elif page == "Portfolio Analysis":
        st.markdown("<h2 class='sub-header'>Portfolio Analysis</h2>", unsafe_allow_html=True)
        
        # Region and sector filters
        col1, col2 = st.columns(2)
        
        with col1:
            region = st.selectbox("Filter by Region", ["All Regions", "North America", "Asia", "Europe", "South America"])
        
        with col2:
            sector = st.selectbox("Filter by Sector", ["All Sectors", "Technology", "Consumer Cyclical", "Communication Services", "Financial Services", "Energy"])
        
        # Apply filters
        region_filter = None if region == "All Regions" else region
        sector_filter = None if sector == "All Sectors" else sector
        
        # Get portfolio data
        with st.spinner("Loading real-time portfolio data..."):
            portfolio_df = get_portfolio_data()
            
            # Apply filters if needed
            if region_filter:
                portfolio_df = portfolio_df[portfolio_df['Region'] == region_filter]
            if sector_filter:
                portfolio_df = portfolio_df[portfolio_df['Sector'] == sector_filter]
        
        # Display portfolio
        st.dataframe(portfolio_df, use_container_width=True)
        
        # Portfolio metrics
        total_value = portfolio_df['Value'].sum()
        
        # Calculate allocation by region and sector
        region_allocation = portfolio_df.groupby('Region')['Value'].sum() / total_value * 100 if total_value > 0 else pd.Series()
        sector_allocation = portfolio_df.groupby('Sector')['Value'].sum() / total_value * 100 if total_value > 0 else pd.Series()
        
        # Display metrics
        st.markdown("<h3 class='sub-header'>Portfolio Metrics</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:,.2f}")
            st.metric("Number of Holdings", len(portfolio_df))
        
        with col2:
            if region_filter and not region_allocation.empty:
                region_pct = region_allocation.get(region_filter, 0)
                st.metric(f"{region_filter} Allocation", f"{region_pct:.2f}%")
            
            if sector_filter and not sector_allocation.empty:
                sector_pct = sector_allocation.get(sector_filter, 0)
                st.metric(f"{sector_filter} Allocation", f"{sector_pct:.2f}%")
        
        # Portfolio visualizations
        st.markdown("<h3 class='sub-header'>Portfolio Allocation</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("By Region")
            if not region_allocation.empty:
                st.bar_chart(region_allocation)
            else:
                st.write("No data available")
        
        with col2:
            st.subheader("By Sector")
            if not sector_allocation.empty:
                st.bar_chart(sector_allocation)
            else:
                st.write("No data available")
    
    elif page == "Earnings Surprises":
        st.markdown("<h2 class='sub-header'>Earnings Surprises</h2>", unsafe_allow_html=True)
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            days = st.slider("Lookback Period (Days)", 7, 90, 30)
        
        with col2:
            sector = st.selectbox("Filter by Sector", ["All Sectors", "Technology", "Consumer Cyclical", "Communication Services", "Financial Services", "Energy"])
        
        # Apply filters
        sector_filter = None if sector == "All Sectors" else sector
        
        # Get earnings data
        with st.spinner("Loading real earnings data..."):
            earnings_df = get_earnings_surprises(days)
            
            # Apply sector filter if needed
            if sector_filter and not earnings_df.empty:
                earnings_df = earnings_df[earnings_df['Sector'] == sector_filter]
        
        # Display earnings surprises
        if not earnings_df.empty:
            st.dataframe(
                earnings_df.style.applymap(
                    lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                    subset=['Surprise %']
                ),
                use_container_width=True
            )
            
            # Visualizations
            st.markdown("<h3 class='sub-header'>Earnings Analysis</h3>", unsafe_allow_html=True)
            
            # Top positive surprises
            st.subheader("Top Positive Surprises")
            top_positive = earnings_df.sort_values(by='Surprise %', ascending=False).head(5)
            st.bar_chart(top_positive.set_index('Symbol')['Surprise %'])
            
            # Top negative surprises
            st.subheader("Top Negative Surprises")
            top_negative = earnings_df.sort_values(by='Surprise %').head(5)
            st.bar_chart(top_negative.set_index('Symbol')['Surprise %'])
        else:
            st.info("No earnings data available for the selected filters.")
    
    # Footer
    st.markdown("---")
    st.markdown("<div class='info-text'>Voice Finance Assistant - Powered by AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-text'>Data provided by Yahoo Finance and Alpha Vantage</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
