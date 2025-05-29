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

# Import our custom VoiceAgent
from agents.voice_agent import VoiceAgent

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

# Initialize voice agent
voice_agent = VoiceAgent()

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

// ... existing code ...

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
