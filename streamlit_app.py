"""
Streamlit app for Finance Assistant.
"""
import os
import tempfile
import logging
import requests
import streamlit as st
from dotenv import load_dotenv
import time
import base64
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = os.getenv("API_PORT", "8000")
API_URL = f"http://{API_HOST}:{API_PORT}"

# App title and configuration
st.set_page_config(
    page_title="Finance Assistant",
    page_icon="💹",
    layout="wide"
)

def check_api_status():
    """Check if the API is online."""
    try:
        response = requests.get(f"{API_URL}/")
        return response.status_code == 200
    except:
        return False

def process_text_query(query):
    """Send a text query to the API and get the response."""
    try:
        logger.info(f"Sending text query to API: {query}")
        response = requests.post(
            f"{API_URL}/query/text",
            json={"text": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Received response from API: {result}")
            
            # Check if response has the expected format
            if "text" not in result:
                st.error("API response missing 'text' field")
                return {
                    "text": "I'm sorry, there was an issue with the response format. Please try again.",
                    "success": False,
                    "error": "Invalid response format"
                }
                
            return result
        else:
            error_msg = f"Error: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - {response.text}"
                
            st.error(error_msg)
            logger.error(f"API error: {error_msg}")
            
            return {
                "text": "I'm sorry, there was an error processing your query. Please try again later.",
                "success": False,
                "error": error_msg
            }
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        st.error(error_msg)
        logger.error(f"Exception in process_text_query: {error_msg}")
        
        return {
            "text": "I'm sorry, there was an error connecting to the API. Please check if the server is running.",
            "success": False,
            "error": error_msg
        }

def process_voice_query(audio_file):
    """Send a voice query to the API and get the response."""
    try:
        # Save uploaded audio to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_file.getvalue())
            tmp_file_path = tmp_file.name
        
        response = requests.post(
            f"{API_URL}/query/voice",
            json={"audio_file_path": tmp_file_path}
        )
        
        # Clean up the temporary file
        os.unlink(tmp_file_path)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def get_audio_recorder_html():
    """Generate HTML/JS code for audio recording."""
    return """
    <script>
    // Audio recording functionality
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let recordingTimer;
    let recordingDuration = 0;
    let audioContext;
    let analyser;
    let microphone;
    
    function startRecording() {
        document.getElementById('recordButton').disabled = true;
        document.getElementById('stopButton').disabled = false;
        document.getElementById('recordingStatus').innerText = "Recording...";
        document.getElementById('recordingStatus').style.color = "#FF4B4B";
        document.getElementById('recordingVisualizer').style.display = "block";
        document.getElementById('processingIndicator').style.display = "none";
        
        // Reset recording duration
        recordingDuration = 0;
        document.getElementById('recordingTime').innerText = "00:00";
        
        // Start timer
        recordingTimer = setInterval(() => {
            recordingDuration += 1;
            const minutes = Math.floor(recordingDuration / 60).toString().padStart(2, '0');
            const seconds = (recordingDuration % 60).toString().padStart(2, '0');
            document.getElementById('recordingTime').innerText = `${minutes}:${seconds}`;
            
            // Auto-stop after 2 minutes to prevent very large files
            if (recordingDuration >= 120) {
                stopRecording();
            }
        }, 1000);
        
        // Reset audio chunks
        audioChunks = [];
        isRecording = true;
        
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
                mediaRecorder.start();
                
                // Set up audio visualization
                setupAudioVisualization(stream);
                
                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });
                
                mediaRecorder.addEventListener("stop", () => {
                    // Show processing indicator
                    document.getElementById('processingIndicator').style.display = "block";
                    
                    // Create audio blob and convert to WAV
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    
                    // Convert to base64
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = () => {
                        const base64data = reader.result.split(',')[1];
                        document.getElementById('audioData').value = base64data;
                        
                        // Automatically trigger the submit button
                        document.getElementById('submitAudioBtn').click();
                    };
                    
                    // Stop all tracks
                    stream.getTracks().forEach(track => track.stop());
                    if (audioContext) {
                        audioContext.close();
                    }
                });
            })
            .catch(err => {
                console.error("Error accessing microphone:", err);
                document.getElementById('recordingStatus').innerText = "Error: " + err.message;
                document.getElementById('recordingStatus').style.color = "#FF4B4B";
                document.getElementById('recordButton').disabled = false;
            });
    }
    
    function setupAudioVisualization(stream) {
        // Create audio context
        audioContext = new AudioContext();
        analyser = audioContext.createAnalyser();
        microphone = audioContext.createMediaStreamSource(stream);
        
        // Connect the microphone to the analyser
        microphone.connect(analyser);
        
        // Configure analyser
        analyser.fftSize = 256;
        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        
        // Get canvas and context
        const canvas = document.getElementById('visualizer');
        const canvasCtx = canvas.getContext('2d');
        const WIDTH = canvas.width;
        const HEIGHT = canvas.height;
        
        // Draw function for visualization
        function draw() {
            if (!isRecording) return;
            
            requestAnimationFrame(draw);
            analyser.getByteFrequencyData(dataArray);
            
            canvasCtx.fillStyle = 'rgb(20, 20, 20)';
            canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);
            
            const barWidth = (WIDTH / bufferLength) * 2.5;
            let barHeight;
            let x = 0;
            
            for (let i = 0; i < bufferLength; i++) {
                barHeight = dataArray[i] / 2;
                
                // Use a gradient color based on amplitude
                const hue = 120 + (barHeight / 50 * 240); // from green to red
                canvasCtx.fillStyle = `hsl(${hue}, 100%, 50%)`;
                canvasCtx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);
                
                x += barWidth + 1;
            }
        }
        
        draw();
    }
    
    function stopRecording() {
        if (!isRecording) return;
        
        isRecording = false;
        clearInterval(recordingTimer);
        
        document.getElementById('recordButton').disabled = false;
        document.getElementById('stopButton').disabled = true;
        document.getElementById('recordingStatus').innerText = "Processing...";
        document.getElementById('recordingStatus').style.color = "#FFA500";
        
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
        }
    }
    </script>
    
    <div style="background-color: #262730; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <div>
                <button id="recordButton" onclick="startRecording()" style="background-color: #FF4B4B; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                    <i class="fas fa-microphone"></i> Start Recording
                </button>
                <button id="stopButton" onclick="stopRecording()" style="background-color: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin-left: 10px;" disabled>
                    <i class="fas fa-stop"></i> Stop Recording
                </button>
            </div>
            <div id="recordingTime" style="font-size: 18px; font-weight: bold; color: white;">00:00</div>
        </div>
        
        <div id="recordingStatus" style="margin: 10px 0; font-size: 16px; color: white;">Ready to record</div>
        
        <div id="processingIndicator" style="display: none; margin: 10px 0;">
            <div style="display: flex; align-items: center;">
                <div style="border: 4px solid #f3f3f3; border-top: 4px solid #3498db; border-radius: 50%; width: 20px; height: 20px; animation: spin 2s linear infinite; margin-right: 10px;"></div>
                <span style="color: #FFA500;">Processing audio... Please wait</span>
            </div>
            <style>
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            </style>
        </div>
        
        <div id="recordingVisualizer" style="display: none; margin-top: 10px;">
            <canvas id="visualizer" width="500" height="60" style="width: 100%; background-color: #1a1a1a; border-radius: 5px;"></canvas>
        </div>
        
        <input type="hidden" id="audioData" name="audioData">
    </div>
    """

def main():
    """Main Streamlit app."""
    st.title("Finance Assistant 💹")
    
    # Check API status
    api_status = check_api_status()
    if api_status:
        st.success("API is online")
    else:
        st.error("API is offline. Please start the API server.")
        st.info("Run: python start.py")
        return
    
    # Sidebar
    st.sidebar.title("Options")
    input_method = st.sidebar.radio("Input Method", ["Text", "Voice"])
    
    if input_method == "Text":
        # Text input
        st.subheader("Text Input")
        
        # Example queries
        st.markdown("### Example Queries")
        example_queries = [
            "What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?",
            "Give me a market brief for today.",
            "How are Asian tech stocks performing today?"
        ]
        
        selected_example = st.selectbox("Select an example query or type your own below:", 
                                      [""] + example_queries)
        
        query = st.text_area("Enter your query:", value=selected_example, height=100)
        
        if st.button("Submit Query"):
            if query:
                with st.spinner("Processing query..."):
                    # Process query
                    result = process_text_query(query)
                    
                    if result:
                        st.markdown("### Response:")
                        st.markdown(result["text"])
                        
                        # Add to chat history
                        if "chat_history" not in st.session_state:
                            st.session_state.chat_history = []
                        
                        st.session_state.chat_history.append({
                            "query": query,
                            "response": result["text"]
                        })
                    else:
                        st.error("Failed to get response from API.")
            else:
                st.warning("Please enter a query.")
    
    else:
        # Voice input
        st.subheader("Voice Input")
        
        tab1, tab2 = st.tabs(["Record Audio", "Upload Audio"])
        
        with tab1:
            # Audio recording
            st.markdown("### Real-time Audio Recording")
            st.markdown("Click the button below to record your voice query:")
            
            # Display audio recorder
            st.components.v1.html(get_audio_recorder_html(), height=350)
            
            # Hidden button to trigger processing
            st.markdown("<style>.stTextInput > label {display: none;}</style>", unsafe_allow_html=True)
            audio_data = st.text_input("Audio data", value="", key="audio_data")
            
            # Create a hidden container for the submit button
            with st.container():
                col1, col2 = st.columns([1, 20])
                with col1:
                    # Make button small and place it in a narrow column
                    submit_button = st.button("Submit Audio", key="submitAudioBtn", help="Process recorded audio")
            
            # Create a placeholder for results
            results_placeholder = st.empty()
            
            if submit_button and audio_data:
                with results_placeholder.container():
                    with st.spinner("Processing audio..."):
                        try:
                            # Decode base64 audio data
                            audio_bytes = base64.b64decode(audio_data)
                            
                            # Save to temporary file
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp_file:
                                tmp_file.write(audio_bytes)
                                tmp_file_path = tmp_file.name
                            
                            # Process audio file
                            response = requests.post(
                                f"{API_URL}/query/voice",
                                json={"audio_file_path": tmp_file_path}
                            )
                            
                            # Clean up
                            os.unlink(tmp_file_path)
                            
                            if response.status_code == 200:
                                result = response.json()
                                
                                # Display recorded audio
                                st.audio(audio_bytes, format="audio/webm")
                                
                                st.markdown("### Transcription:")
                                if result.get("transcription"):
                                    st.info(result["transcription"])
                                else:
                                    st.warning("No transcription available")
                                
                                st.markdown("### Response:")
                                if result.get("text"):
                                    st.success(result["text"])
                                    
                                    # Play audio response if available
                                    if result.get("audio_file_path"):
                                        with open(result["audio_file_path"], "rb") as f:
                                            audio_response = f.read()
                                        st.audio(audio_response, format="audio/mp3")
                                else:
                                    st.error("No response received")
                                    
                                # Add to chat history
                                if "chat_history" not in st.session_state:
                                    st.session_state.chat_history = []
                                
                                st.session_state.chat_history.append({
                                    "query": result.get("transcription", "Voice query"),
                                    "response": result.get("text", "No response")
                                })
                            else:
                                st.error(f"Error: {response.status_code} - {response.text}")
                        except Exception as e:
                            st.error(f"Error processing audio: {e}")
        
        with tab2:
            # File upload option
            st.markdown("### Upload Audio File")
            st.info("Upload an audio file with your query (WAV, MP3, or WEBM format).")
            
            audio_file = st.file_uploader("Upload audio file", type=["wav", "mp3", "webm"])
            
            if audio_file:
                st.audio(audio_file)
                
                if st.button("Process Audio", type="primary"):
                    with st.spinner("Processing audio..."):
                        # Process audio
                        result = process_voice_query(audio_file)
                        
                        if result:
                            st.markdown("### Transcription:")
                            if result.get("transcription"):
                                st.info(result["transcription"])
                            else:
                                st.warning("No transcription available")
                            
                            st.markdown("### Response:")
                            if result.get("text"):
                                st.success(result["text"])
                                
                                # Play audio response if available
                                if result.get("audio_file_path"):
                                    with open(result["audio_file_path"], "rb") as f:
                                        audio_response = f.read()
                                    st.audio(audio_response, format="audio/mp3")
                            else:
                                st.error("No response received")
                            
                            # Add to chat history
                            if "chat_history" not in st.session_state:
                                st.session_state.chat_history = []
                            
                            st.session_state.chat_history.append({
                                "query": result.get("transcription", "Voice query"),
                                "response": result.get("text", "No response")
                            })
                        else:
                            st.error("Failed to process audio.")
    
    # Chat history
    if "chat_history" in st.session_state and st.session_state.chat_history:
        st.markdown("---")
        st.subheader("Chat History")
        
        for i, chat in enumerate(st.session_state.chat_history):
            st.markdown(f"**Query {i+1}:** {chat['query']}")
            st.markdown(f"**Response {i+1}:** {chat['response']}")
            st.markdown("---")

if __name__ == "__main__":
    main() 