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
import yfinance as yf"""
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# App title and configuration
st.set_page_config(
    page_title="Voice Finance Assistant",
    page_icon="🎙️",
    layout="wide"
)

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
        background-color: #e3f2fd;
        border-left: 4px solid #1E88E5;
    }
    .assistant-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

def text_to_speech(text):
    """Convert text to speech and return audio bytes."""
    try:
        tts = gtts.gTTS(text=text, lang="en")
        audio_bytes_io = BytesIO()
        tts.write_to_fp(audio_bytes_io)
        audio_bytes_io.seek(0)
        return audio_bytes_io.read()
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {e}")
        return None

def process_query(query):
    """Process a text query and return a response."""
    if "asia" in query.lower() and "tech" in query.lower():
        return "Your Asia tech allocation is currently 22% of your total portfolio value, up from 18% yesterday. Top holdings in this segment include Taiwan Semiconductor (7.5%), Alibaba Group (5.2%), and Samsung Electronics (4.8%)."
    elif "earnings" in query.lower() or "surprises" in query.lower():
        return "In the technology sector, 65% of companies beat earnings expectations. Taiwan Semiconductor beat estimates by 4.2%, while Samsung missed estimates by 2.1%."
    elif "market" in query.lower() or "overview" in query.lower():
        return "Overall market sentiment today is cautiously bullish. The S&P 500 is up 0.8%, the Dow Jones is up 0.5%, and the NASDAQ is up 1.2%. The best performing sector is Technology at 1.8%."
    else:
        return f"I understand you're asking about: {query}\n\nTo get specific financial information, try asking about market overview, portfolio exposure (especially in regions like Asia or sectors like Technology), or recent earnings surprises."

def get_market_overview():
    """Get an overview of major market indices."""
    # Return dummy data for demonstration
    return pd.DataFrame([
        {"Index": "Dow Jones", "Price": 34567.89, "Change": 123.45, "Change %": 0.36},
        {"Index": "S&P 500", "Price": 4567.89, "Change": 23.45, "Change %": 0.52},
        {"Index": "NASDAQ", "Price": 14567.89, "Change": 123.45, "Change %": 0.85},
        {"Index": "Nikkei 225", "Price": 28567.89, "Change": -123.45, "Change %": -0.43},
        {"Index": "Hang Seng", "Price": 24567.89, "Change": -23.45, "Change %": -0.10},
        {"Index": "FTSE 100", "Price": 7567.89, "Change": 23.45, "Change %": 0.31}
    ])

def get_portfolio_exposure(region=None, sector=None):
    """Get portfolio exposure data."""
    # Return dummy data for demonstration
    return pd.DataFrame([
        {"Symbol": "AAPL", "Name": "Apple Inc.", "Value": 120000, "Shares": 500, "Sector": "Technology", "Region": "North America"},
        {"Symbol": "MSFT", "Name": "Microsoft Corp.", "Value": 100000, "Shares": 300, "Sector": "Technology", "Region": "North America"},
        {"Symbol": "TSM", "Name": "Taiwan Semiconductor", "Value": 40000, "Shares": 400, "Sector": "Technology", "Region": "Asia"},
        {"Symbol": "9988.HK", "Name": "Alibaba Group", "Value": 35000, "Shares": 1500, "Sector": "Consumer Cyclical", "Region": "Asia"},
        {"Symbol": "SONY", "Name": "Sony Group Corp.", "Value": 22000, "Shares": 250, "Sector": "Technology", "Region": "Asia"}
    ])

def get_earnings_surprises(days=30, sector=None):
    """Get earnings surprises data."""
    # Return dummy data for demonstration
    return pd.DataFrame([
        {"Symbol": "AAPL", "Company": "Apple Inc.", "Expected EPS": 1.45, "Actual EPS": 1.52, "Surprise %": 4.83, "Date": "2023-04-28", "Sector": "Technology"},
        {"Symbol": "MSFT", "Company": "Microsoft Corp.", "Expected EPS": 2.23, "Actual EPS": 2.35, "Surprise %": 5.38, "Date": "2023-04-25", "Sector": "Technology"},
        {"Symbol": "GOOGL", "Company": "Alphabet Inc.", "Expected EPS": 1.34, "Actual EPS": 1.44, "Surprise %": 7.46, "Date": "2023-04-25", "Sector": "Communication Services"},
        {"Symbol": "META", "Company": "Meta Platforms Inc.", "Expected EPS": 2.56, "Actual EPS": 2.20, "Surprise %": -14.06, "Date": "2023-04-26", "Sector": "Communication Services"},
        {"Symbol": "AMZN", "Company": "Amazon.com Inc.", "Expected EPS": 0.21, "Actual EPS": 0.31, "Surprise %": 47.62, "Date": "2023-04-27", "Sector": "Consumer Cyclical"}
    ])

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
        
        # Create a line chart with dummy data
        dates = pd.date_range(end=datetime.datetime.now(), periods=180)
        values = np.random.randn(180).cumsum() + 4500
        chart_data = pd.DataFrame({'Date': dates, 'Value': values})
        chart_data = chart_data.set_index('Date')
        
        st.line_chart(chart_data)
        st.caption("S&P 500 - 6 Month Trend")
    
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
        with st.spinner("Loading portfolio data..."):
            portfolio_df = get_portfolio_exposure(region_filter, sector_filter)
        
        # Display portfolio
        st.dataframe(portfolio_df, use_container_width=True)
        
        # Portfolio metrics
        total_value = portfolio_df['Value'].sum()
        
        # Calculate allocation by region and sector
        region_allocation = portfolio_df.groupby('Region')['Value'].sum() / total_value * 100
        sector_allocation = portfolio_df.groupby('Sector')['Value'].sum() / total_value * 100
        
        # Display metrics
        st.markdown("<h3 class='sub-header'>Portfolio Metrics</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:,.2f}")
            st.metric("Number of Holdings", len(portfolio_df))
        
        with col2:
            if region_filter:
                region_pct = region_allocation.get(region_filter, 0)
                st.metric(f"{region_filter} Allocation", f"{region_pct:.2f}%")
            
            if sector_filter:
                sector_pct = sector_allocation.get(sector_filter, 0)
                st.metric(f"{sector_filter} Allocation", f"{sector_pct:.2f}%")
        
        # Portfolio visualizations
        st.markdown("<h3 class='sub-header'>Portfolio Allocation</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("By Region")
            st.bar_chart(region_allocation)
        
        with col2:
            st.subheader("By Sector")
            st.bar_chart(sector_allocation)
    
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
        with st.spinner("Loading earnings data..."):
            earnings_df = get_earnings_surprises(days, sector_filter)
        
        # Display earnings surprises
        st.dataframe(
            earnings_df.style.applymap(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                subset=['Surprise %']
            ),
            use_container_width=True
        )
        
        # Visualizations
        st.markdown("<h3 class='sub-header'>Earnings Analysis</h3>", unsafe_allow_html=True)
        
        if not earnings_df.empty:
            # Top positive surprises
            st.subheader("Top Positive Surprises")
            top_positive = earnings_df.sort_values(by='Surprise %', ascending=False).head(5)
            st.bar_chart(top_positive.set_index('Symbol')['Surprise %'])
            
            # Top negative surprises
            st.subheader("Top Negative Surprises")
            top_negative = earnings_df.sort_values(by='Surprise %').head(5)
            st.bar_chart(top_negative.set_index('Symbol')['Surprise %'])
    
    # Footer
    st.markdown("---")
    st.markdown("<div class='info-text'>Voice Finance Assistant - Powered by AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-text'>Data provided for informational purposes only. Not financial advice.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
import json
import base64
from data_ingestion.web_scraper import WebScraper
from data_ingestion.market_data import MarketDataClient
from data_ingestion.vector_store import VectorStore
import requests
from io import BytesIO
import gtts
from pydub import AudioSegment
from pydub.playback import play
import threading
from agents.orchestrator import AgentOrchestrator
from agents.voice_agent import VoiceAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize data clients and agents
web_scraper = WebScraper()
market_data_client = MarketDataClient()
vector_store = VectorStore()
voice_agent = VoiceAgent()
orchestrator = AgentOrchestrator(market_data_client, web_scraper, vector_store)

# App title and configuration
st.set_page_config(
    page_title="Voice Finance Assistant",
    page_icon="🎙️",
    layout="wide"
)

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
        background-color: #e3f2fd;
        border-left: 4px solid #1E88E5;
    }
    .assistant-message {
        background-color: #f1f8e9;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

def text_to_speech(text):
    """Convert text to speech and return audio bytes."""
    try:
        tts = gtts.gTTS(text=text, lang="en")
        audio_bytes_io = BytesIO()
        tts.write_to_fp(audio_bytes_io)
        audio_bytes_io.seek(0)
        return audio_bytes_io.read()
    except Exception as e:
        logger.error(f"Error in text-to-speech conversion: {e}")
        return None

def process_voice_query(audio_bytes):
    """Process voice query and return response."""
    try:
        # Convert speech to text using the voice agent
        query_text = voice_agent.speech_to_text(audio_bytes)
        if not query_text:
            return "Sorry, I couldn't understand what you said. Please try again."
        
        st.session_state.last_query = query_text
        
        # Process the query through the orchestrator
        response = orchestrator.process_query(query_text)
        
        # Add to conversation history
        st.session_state.conversation_history.append({"role": "user", "content": query_text})
        st.session_state.conversation_history.append({"role": "assistant", "content": response})
        
        st.session_state.last_response = response
        
        # Convert response to speech
        audio_bytes = text_to_speech(response)
        st.session_state.audio_bytes = audio_bytes
        
        return response
    except Exception as e:
        logger.error(f"Error processing voice query: {e}")
        return f"An error occurred: {str(e)}"

def get_market_overview():
    """Get an overview of major market indices."""
    try:
        # Get market data from the market data client
        market_summary = market_data_client.get_market_summary()
        
        # Create a DataFrame for display
        data = []
        for index_info in market_summary.get("indices", []):
            data.append({
                "Index": index_info.get("name", "Unknown"),
                "Price": index_info.get("price", 0),
                "Change": index_info.get("change", 0),
                "Change %": index_info.get("change_percent", 0)
            })
        
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error getting market overview: {e}")
        # Return dummy data if there's an error
        return pd.DataFrame([
            {"Index": "Dow Jones", "Price": 34567.89, "Change": 123.45, "Change %": 0.36},
            {"Index": "S&P 500", "Price": 4567.89, "Change": 23.45, "Change %": 0.52},
            {"Index": "NASDAQ", "Price": 14567.89, "Change": 123.45, "Change %": 0.85},
            {"Index": "Nikkei 225", "Price": 28567.89, "Change": -123.45, "Change %": -0.43},
            {"Index": "Hang Seng", "Price": 24567.89, "Change": -23.45, "Change %": -0.10},
            {"Index": "FTSE 100", "Price": 7567.89, "Change": 23.45, "Change %": 0.31}
        ])

def get_portfolio_exposure(region=None, sector=None):
    """Get portfolio exposure data."""
    try:
        # Get portfolio data from the market data client
        portfolio_data = market_data_client.get_portfolio_exposure(region, sector)
        
        # Extract the portfolio holdings
        holdings = portfolio_data.get("portfolio", [])
        
        # Create a DataFrame for display
        data = []
        for holding in holdings:
            data.append({
                "Symbol": holding.get("symbol", ""),
                "Name": holding.get("name", ""),
                "Value": holding.get("value", 0),
                "Shares": holding.get("shares", 0),
                "Sector": holding.get("sector", ""),
                "Region": holding.get("region", "")
            })
        
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error getting portfolio exposure: {e}")
        # Return dummy data if there's an error
        return pd.DataFrame([
            {"Symbol": "AAPL", "Name": "Apple Inc.", "Value": 120000, "Shares": 500, "Sector": "Technology", "Region": "North America"},
            {"Symbol": "MSFT", "Name": "Microsoft Corp.", "Value": 100000, "Shares": 300, "Sector": "Technology", "Region": "North America"},
            {"Symbol": "TSM", "Name": "Taiwan Semiconductor", "Value": 40000, "Shares": 400, "Sector": "Technology", "Region": "Asia"},
            {"Symbol": "9988.HK", "Name": "Alibaba Group", "Value": 35000, "Shares": 1500, "Sector": "Consumer Cyclical", "Region": "Asia"},
            {"Symbol": "SONY", "Name": "Sony Group Corp.", "Value": 22000, "Shares": 250, "Sector": "Technology", "Region": "Asia"}
        ])

def get_earnings_surprises(days=30, sector=None):
    """Get earnings surprises data."""
    try:
        # Get earnings data from the market data client
        earnings_data = market_data_client.get_earnings_surprises(days, sector)
        
        # Extract the surprises
        surprises = earnings_data.get("surprises", [])
        
        # Create a DataFrame for display
        data = []
        for surprise in surprises:
            data.append({
                "Symbol": surprise.get("symbol", ""),
                "Company": surprise.get("name", ""),
                "Expected EPS": surprise.get("expected_eps", 0),
                "Actual EPS": surprise.get("actual_eps", 0),
                "Surprise %": surprise.get("surprise_percent", 0),
                "Date": surprise.get("date", ""),
                "Sector": surprise.get("sector", "")
            })
        
        return pd.DataFrame(data)
    except Exception as e:
        logger.error(f"Error getting earnings surprises: {e}")
        # Return dummy data if there's an error
        return pd.DataFrame([
            {"Symbol": "AAPL", "Company": "Apple Inc.", "Expected EPS": 1.45, "Actual EPS": 1.52, "Surprise %": 4.83, "Date": "2023-04-28", "Sector": "Technology"},
            {"Symbol": "MSFT", "Company": "Microsoft Corp.", "Expected EPS": 2.23, "Actual EPS": 2.35, "Surprise %": 5.38, "Date": "2023-04-25", "Sector": "Technology"},
            {"Symbol": "GOOGL", "Company": "Alphabet Inc.", "Expected EPS": 1.34, "Actual EPS": 1.44, "Surprise %": 7.46, "Date": "2023-04-25", "Sector": "Communication Services"},
            {"Symbol": "META", "Company": "Meta Platforms Inc.", "Expected EPS": 2.56, "Actual EPS": 2.20, "Surprise %": -14.06, "Date": "2023-04-26", "Sector": "Communication Services"},
            {"Symbol": "AMZN", "Company": "Amazon.com Inc.", "Expected EPS": 0.21, "Actual EPS": 0.31, "Surprise %": 47.62, "Date": "2023-04-27", "Sector": "Consumer Cyclical"}
        ])

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
                    response = orchestrator.process_query(st.session_state.last_query)
                    st.session_state.last_response = response
                    
                    # Add to conversation history
                    st.session_state.conversation_history.append({"role": "user", "content": st.session_state.last_query})
                    st.session_state.conversation_history.append({"role": "assistant", "content": response})
                    
                    # Generate audio response
                    st.session_state.audio_bytes = text_to_speech(response)
        
        with col2:
            # Text input as an alternative
            text_query = st.text_input("Or type your query:", key="text_query")
            if st.button("Submit"):
                if text_query:
                    with st.spinner("Processing..."):
                        st.session_state.last_query = text_query
                        
                        # Process the query
                        response = orchestrator.process_query(text_query)
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
                sp500_data = yf.Ticker("^GSPC").history(period="6mo")
                
                # Create a line chart
                st.line_chart(sp500_data['Close'])
                st.caption("S&P 500 - 6 Month Trend")
            except Exception as e:
                st.error(f"Error loading market trends: {e}")
    
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
        with st.spinner("Loading portfolio data..."):
            portfolio_df = get_portfolio_exposure(region_filter, sector_filter)
        
        # Display portfolio
        st.dataframe(portfolio_df, use_container_width=True)
        
        # Portfolio metrics
        total_value = portfolio_df['Value'].sum()
        
        # Calculate allocation by region and sector
        region_allocation = portfolio_df.groupby('Region')['Value'].sum() / total_value * 100
        sector_allocation = portfolio_df.groupby('Sector')['Value'].sum() / total_value * 100
        
        # Display metrics
        st.markdown("<h3 class='sub-header'>Portfolio Metrics</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Portfolio Value", f"${total_value:,.2f}")
            st.metric("Number of Holdings", len(portfolio_df))
        
        with col2:
            if region_filter:
                region_pct = region_allocation.get(region_filter, 0)
                st.metric(f"{region_filter} Allocation", f"{region_pct:.2f}%")
            
            if sector_filter:
                sector_pct = sector_allocation.get(sector_filter, 0)
                st.metric(f"{sector_filter} Allocation", f"{sector_pct:.2f}%")
        
        # Portfolio visualizations
        st.markdown("<h3 class='sub-header'>Portfolio Allocation</h3>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("By Region")
            st.bar_chart(region_allocation)
        
        with col2:
            st.subheader("By Sector")
            st.bar_chart(sector_allocation)
    
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
        with st.spinner("Loading earnings data..."):
            earnings_df = get_earnings_surprises(days, sector_filter)
        
        # Display earnings surprises
        st.dataframe(
            earnings_df.style.applymap(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x > 0 else ('color: red' if isinstance(x, (int, float)) and x < 0 else ''),
                subset=['Surprise %']
            ),
            use_container_width=True
        )
        
        # Visualizations
        st.markdown("<h3 class='sub-header'>Earnings Analysis</h3>", unsafe_allow_html=True)
        
        if not earnings_df.empty:
            # Top positive surprises
            st.subheader("Top Positive Surprises")
            top_positive = earnings_df.sort_values(by='Surprise %', ascending=False).head(5)
            st.bar_chart(top_positive.set_index('Symbol')['Surprise %'])
            
            # Top negative surprises
            st.subheader("Top Negative Surprises")
            top_negative = earnings_df.sort_values(by='Surprise %').head(5)
            st.bar_chart(top_negative.set_index('Symbol')['Surprise %'])
    
    # Footer
    st.markdown("---")
    st.markdown("<div class='info-text'>Voice Finance Assistant - Powered by AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='info-text'>Data provided for informational purposes only. Not financial advice.</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
