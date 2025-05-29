"""
Startup script for the Finance Assistant application.
Launches both the API server and Streamlit app.
"""
import os
import subprocess
import time
import sys
import logging
import socket
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def find_available_port(start_port, max_attempts=10):
    """Find an available port starting from start_port."""
    port = start_port
    for _ in range(max_attempts):
        if not is_port_in_use(port):
            return port
        port += 1
    raise RuntimeError(f"Could not find an available port after {max_attempts} attempts")

def start_api_server():
    """Start the API server."""
    logger.info("Starting API server...")
    
    # Get API port from environment variables or use default
    api_port = int(os.getenv("API_PORT", "8000"))
    
    # Find an available port
    try:
        if is_port_in_use(api_port):
            new_port = find_available_port(api_port + 1)
            logger.info(f"Port {api_port} is in use. Using port {new_port} instead.")
            os.environ["API_PORT"] = str(new_port)
            api_port = new_port
        
        # Use subprocess to start the API server in a new process
        api_process = subprocess.Popen(
            [sys.executable, "orchestrator/main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()  # Pass updated environment variables
        )
        logger.info(f"API server started on port {api_port}.")
        return api_process, api_port
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        sys.exit(1)

def start_streamlit_app():
    """Start the Streamlit app."""
    logger.info("Starting Streamlit app...")
    
    # Get streamlit port from environment variables
    streamlit_port = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    # Find an available port
    try:
        if is_port_in_use(streamlit_port):
            new_port = find_available_port(streamlit_port + 1)
            logger.info(f"Port {streamlit_port} is in use. Using port {new_port} instead.")
            streamlit_port = new_port
        
        # Use subprocess to start the Streamlit app in a new process
        streamlit_process = subprocess.Popen(
            [
                sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
                "--server.port", str(streamlit_port)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy()  # Pass updated environment variables
        )
        logger.info(f"Streamlit app started on port {streamlit_port}.")
        return streamlit_process, streamlit_port
    except Exception as e:
        logger.error(f"Error starting Streamlit app: {e}")
        sys.exit(1)

def main():
    """Start all components of the application."""
    logger.info("Starting Finance Assistant application...")
    
    # Start API server
    api_process, api_port = start_api_server()
    
    # Wait for API server to initialize (adjust time as needed)
    logger.info("Waiting for API server to initialize...")
    time.sleep(5)
    
    # Update the API URL environment variable for Streamlit
    os.environ["API_HOST"] = "localhost"
    os.environ["API_PORT"] = str(api_port)
    
    # Start Streamlit app
    streamlit_process, streamlit_port = start_streamlit_app()
    
    logger.info("All components started successfully.")
    logger.info(f"API server running on http://localhost:{api_port}")
    logger.info(f"Streamlit app running on http://localhost:{streamlit_port}")
    logger.info("Press Ctrl+C to stop all processes.")
    
    try:
        # Keep the script running
        while True:
            # Check if processes are still running
            if api_process.poll() is not None:
                logger.error("API server has stopped unexpectedly.")
                streamlit_process.terminate()
                sys.exit(1)
            
            if streamlit_process.poll() is not None:
                logger.error("Streamlit app has stopped unexpectedly.")
                api_process.terminate()
                sys.exit(1)
                
            time.sleep(1)
    except KeyboardInterrupt:
        # Handle Ctrl+C
        logger.info("Stopping all processes...")
        api_process.terminate()
        streamlit_process.terminate()
        logger.info("All processes stopped.")

if __name__ == "__main__":
    main() 