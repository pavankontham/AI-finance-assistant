"""
Streamlit app for the Finance Assistant.
"""
import os
import logging
import json
import base64
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}"

# Page configuration
st.set_page_config(
    page_title="Finance Assistant",
    page_icon="💹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar
st.sidebar.title("Finance Assistant")
st.sidebar.image("https://img.icons8.com/color/96/000000/financial-growth.png", width=100)

query_type = st.sidebar.selectbox(
    "Query Type",
    ["Market Brief", "Stock Information", "General Question"],
    index=0
)

input_mode = st.sidebar.radio(
    "Input Mode",
    ["Text", "Voice"],
    index=0
)

st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.info(
    "This is a multi-agent finance assistant that provides market insights "
    "through both text and voice interactions. It can answer questions about "
    "portfolio exposure, earnings surprises, and market sentiment."
)

# Main content
st.title("Finance Assistant")

if query_type == "Market Brief":
    st.subheader("Market Brief")
    st.write(
        "Ask about market trends, portfolio exposure, earnings surprises, or sector performance. "
        "For example: 'What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?'"
    )
    query_type_value = "market_brief"
elif query_type == "Stock Information":
    st.subheader("Stock Information")
    st.write(
        "Ask about specific stocks by including the ticker symbol in your question. "
        "For example: 'How is AAPL performing today?' or 'What's the latest news on TSLA?'"
    )
    query_type_value = "stock_info"
else:
    st.subheader("General Question")
    st.write(
        "Ask any finance-related question. "
        "For example: 'What are the major factors affecting the bond market right now?'"
    )
    query_type_value = "general"

# Input area
if input_mode == "Text":
    query_text = st.text_area("Enter your question:", height=100)
    generate_audio = st.checkbox("Generate voice response", value=False)
    
    if st.button("Submit", type="primary"):
        if query_text:
            with st.spinner("Processing your query..."):
                try:
                    # Call the API
                    response = requests.post(
                        f"{API_URL}/text-query",
                        json={
                            "text": query_text,
                            "query_type": query_type_value,
                            "parameters": {"generate_audio": generate_audio}
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display the response
                        st.markdown("### Response:")
                        st.write(result["response"])
                        
                        # Play audio if available
                        if generate_audio and result.get("audio_data"):
                            audio_data = base64.b64decode(result["audio_data"])
                            st.audio(audio_data, format="audio/wav")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                
                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
        else:
            st.warning("Please enter a question.")
else:  # Voice input
    st.write("Voice input is simulated in this demo. In a real implementation, this would use your microphone.")
    
    # Simulated voice input
    uploaded_file = st.file_uploader("Upload an audio file (WAV format)", type=["wav"])
    
    if uploaded_file is not None:
        # Display the audio file
        st.audio(uploaded_file, format="audio/wav")
        
        if st.button("Process Audio", type="primary"):
            with st.spinner("Processing your audio..."):
                try:
                    # Convert the uploaded file to base64
                    audio_bytes = uploaded_file.getvalue()
                    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                    
                    # Call the API
                    response = requests.post(
                        f"{API_URL}/voice-query",
                        json={
                            "audio_data": audio_b64,
                            "query_type": query_type_value,
                            "parameters": {}
                        }
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        
                        # Display the transcription
                        st.markdown("### Transcription:")
                        st.write(result["query"])
                        
                        # Display the response
                        st.markdown("### Response:")
                        st.write(result["response"])
                        
                        # Play audio response
                        if result.get("audio_data"):
                            audio_data = base64.b64decode(result["audio_data"])
                            st.audio(audio_data, format="audio/wav")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")
    else:
        st.info("Upload a WAV file to simulate voice input.")

# Example queries
st.markdown("---")
st.subheader("Example Queries")

example_queries = [
    "What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?",
    "How is AAPL performing compared to the tech sector?",
    "What are the major factors affecting the bond market right now?",
    "Which sectors are showing the strongest performance this week?"
]

for i, query in enumerate(example_queries):
    if st.button(f"Try: {query}", key=f"example_{i}"):
        # Set the query text and submit
        if input_mode == "Text":
            st.session_state.query_text = query
            st.rerun()

# Display a sample response for the main use case
if not st.session_state.get("displayed_sample") and query_type == "Market Brief" and input_mode == "Text":
    st.markdown("---")
    st.subheader("Sample Response")
    st.markdown(
        "> Today, your Asia tech allocation is 22% of AUM, up from 18% yesterday. "
        "TSMC beat estimates by 4%, Samsung missed by 2%. Regional sentiment is "
        "neutral with a cautionary tilt due to rising yields."
    )
    st.session_state.displayed_sample = True 