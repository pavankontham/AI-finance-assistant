"""
Voice Agent Module
Handles speech-to-text and text-to-speech functionality with improved accuracy.
"""
import logging
import os
from io import BytesIO

import gtts
from pydub import AudioSegment
import speech_recognition as sr

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceAgent:
    """
    A voice agent that handles speech-to-text and text-to-speech functionality.
    Provides improved accuracy for audio processing.
    """
    
    def __init__(self):
        """Initialize the VoiceAgent."""
        self.recognizer = sr.Recognizer()
        # Adjust recognition parameters for better accuracy
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.pause_threshold = 0.8
        self.recognizer.operation_timeout = 10  # seconds
        
    def speech_to_text(self, audio_file):
        """
        Convert speech from an audio file to text.
        
        Args:
            audio_file: The audio file to process (bytes or file path)
            
        Returns:
            str: The transcribed text or None if an error occurred
        """
        try:
            # Handle different input types
            if isinstance(audio_file, bytes):
                # Convert bytes to an AudioData object
                with BytesIO(audio_file) as audio_io:
                    # Convert to wav format for better compatibility
                    audio = AudioSegment.from_file(audio_io)
                    wav_io = BytesIO()
                    audio.export(wav_io, format="wav")
                    wav_io.seek(0)
                    with sr.AudioFile(wav_io) as source:
                        audio_data = self.recognizer.record(source)
            elif isinstance(audio_file, str) and os.path.exists(audio_file):
                # Load from file path
                with sr.AudioFile(audio_file) as source:
                    audio_data = self.recognizer.record(source)
            else:
                logger.error("Invalid audio file format")
                return None
                
            # Try multiple recognition services for better accuracy
            try:
                # Try Google's speech recognition first (requires internet)
                text = self.recognizer.recognize_google(audio_data)
                logger.info("Successfully transcribed audio using Google Speech Recognition")
                return text
            except sr.RequestError:
                # Fall back to Sphinx (offline, less accurate but works without internet)
                try:
                    text = self.recognizer.recognize_sphinx(audio_data)
                    logger.info("Successfully transcribed audio using Sphinx (offline)")
                    return text
                except Exception as e:
                    logger.error(f"Sphinx recognition error: {e}")
                    return None
            except Exception as e:
                logger.error(f"Speech recognition error: {e}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            return None
    
    def text_to_speech(self, text, lang="en", slow=False):
        """
        Convert text to speech.
        
        Args:
            text (str): The text to convert to speech
            lang (str): The language code (default: "en")
            slow (bool): Whether to speak slowly (default: False)
            
        Returns:
            bytes: The audio bytes or None if an error occurred
        """
        try:
            tts = gtts.gTTS(text=text, lang=lang, slow=slow)
            audio_bytes_io = BytesIO()
            tts.write_to_fp(audio_bytes_io)
            audio_bytes_io.seek(0)
            return audio_bytes_io.read()
        except Exception as e:
            logger.error(f"Error in text-to-speech conversion: {e}")
            return None

# Example usage
if __name__ == "__main__":
    voice_agent = VoiceAgent()
    
    # Example text-to-speech
    audio_bytes = voice_agent.text_to_speech("Hello, I'm your finance assistant. How can I help you today?")
    
    # Save to file for testing
    if audio_bytes:
        with open("test_output.mp3", "wb") as f:
            f.write(audio_bytes)
        print("Audio saved to test_output.mp3")
