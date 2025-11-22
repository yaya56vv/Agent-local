"""
Voice Service - Speech recognition (input) and TTS (output)
Supports push-to-talk via F2 hotkey
"""
import logging
import threading
import time
from typing import Optional, Callable
import speech_recognition as sr
import pyttsx3
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class VoiceService(QObject):
    """
    Handles voice input (speech recognition) and output (TTS).
    Push-to-talk mode with F2 hotkey.
    """
    
    # Signals for thread-safe UI updates
    listening_started = Signal()
    listening_stopped = Signal()
    transcription_ready = Signal(str)  # transcribed text
    speaking_started = Signal(str)  # text being spoken
    speaking_stopped = Signal()
    error_occurred = Signal(str)  # error message
    
    def __init__(self):
        super().__init__()
        
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening_active = False
        self.listen_thread = None
        
        # TTS
        self.tts_engine = None
        self.is_speaking_active = False
        self.speak_thread = None
        
        # Configuration
        self.listen_timeout = 10  # seconds
        self.phrase_time_limit = 10  # seconds
        
        self._initialize_services()
        
    def _initialize_services(self):
        """Initialize speech recognition and TTS"""
        try:
            # Initialize microphone
            self.microphone = sr.Microphone()
            logger.info("Microphone initialized")
            
            # Adjust for ambient noise (calibration)
            with self.microphone as source:
                logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Microphone calibrated")
                
        except Exception as e:
            logger.error(f"Failed to initialize microphone: {e}")
            self.error_occurred.emit(f"Erreur micro : {str(e)}")
            
        try:
            # Initialize TTS engine
            self.tts_engine = pyttsx3.init()
            
            # Configure TTS
            self.tts_engine.setProperty('rate', 175)  # Speed (words per minute)
            self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            if voices:
                # Try to use a French voice if available
                for voice in voices:
                    if 'french' in voice.name.lower() or 'fr' in voice.id.lower():
                        self.tts_engine.setProperty('voice', voice.id)
                        logger.info(f"Using French voice: {voice.name}")
                        break
                else:
                    # Use first available voice
                    self.tts_engine.setProperty('voice', voices[0].id)
                    logger.info(f"Using default voice: {voices[0].name}")
                    
            logger.info("TTS engine initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize TTS: {e}")
            self.error_occurred.emit(f"Erreur TTS : {str(e)}")
            
    def start_listening(self):
        """Start listening for voice input (push-to-talk)"""
        if self.is_listening_active:
            logger.warning("Already listening")
            return
            
        if not self.microphone:
            logger.error("Microphone not initialized")
            self.error_occurred.emit("Microphone non disponible")
            return
            
        self.is_listening_active = True
        self.listening_started.emit()
        
        # Start listening in separate thread
        self.listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listen_thread.start()
        
        logger.info("Voice listening started")
        
    def stop_listening(self):
        """Stop listening for voice input"""
        if not self.is_listening_active:
            return
            
        self.is_listening_active = False
        self.listening_stopped.emit()
        
        # Wait for thread to finish
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2.0)
            
        logger.info("Voice listening stopped")
        
    def is_listening(self) -> bool:
        """Check if currently listening"""
        return self.is_listening_active
        
    def _listen_loop(self):
        """Listen for voice input and transcribe"""
        try:
            with self.microphone as source:
                logger.info("Listening for speech...")
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=self.listen_timeout,
                    phrase_time_limit=self.phrase_time_limit
                )
                
                if not self.is_listening_active:
                    return
                    
                logger.info("Audio captured, transcribing...")
                
                # Transcribe using Google Speech Recognition (free)
                try:
                    text = self.recognizer.recognize_google(audio, language='fr-FR')
                    logger.info(f"Transcribed: {text}")
                    self.transcription_ready.emit(text)
                    
                except sr.UnknownValueError:
                    logger.warning("Could not understand audio")
                    self.error_occurred.emit("Je n'ai pas compris")
                    
                except sr.RequestError as e:
                    logger.error(f"Speech recognition error: {e}")
                    self.error_occurred.emit(f"Erreur de reconnaissance : {str(e)}")
                    
        except sr.WaitTimeoutError:
            logger.warning("Listening timeout - no speech detected")
            self.error_occurred.emit("Aucune parole détectée")
            
        except Exception as e:
            logger.error(f"Error in listen loop: {e}", exc_info=True)
            self.error_occurred.emit(f"Erreur : {str(e)}")
            
        finally:
            self.is_listening_active = False
            self.listening_stopped.emit()
            
    def speak(self, text: str):
        """
        Speak text using TTS (text-to-speech)
        
        Args:
            text: Text to speak
        """
        if not text or not text.strip():
            logger.warning("Empty text provided for TTS")
            return
            
        if not self.tts_engine:
            logger.error("TTS engine not initialized")
            self.error_occurred.emit("TTS non disponible")
            return
            
        if self.is_speaking_active:
            logger.warning("Already speaking, stopping previous speech")
            self.stop_speaking()
            time.sleep(0.2)
            
        self.is_speaking_active = True
        self.speaking_started.emit(text)
        
        # Speak in separate thread
        self.speak_thread = threading.Thread(
            target=self._speak_loop,
            args=(text,),
            daemon=True
        )
        self.speak_thread.start()
        
        logger.info(f"TTS started: {text[:50]}...")
        
    def stop_speaking(self):
        """Stop current TTS playback"""
        if not self.is_speaking_active:
            return
            
        self.is_speaking_active = False
        
        try:
            if self.tts_engine:
                self.tts_engine.stop()
        except Exception as e:
            logger.error(f"Error stopping TTS: {e}")
            
        self.speaking_stopped.emit()
        logger.info("TTS stopped")
        
    def _speak_loop(self, text: str):
        """TTS loop (runs in separate thread)"""
        try:
            if self.tts_engine and self.is_speaking_active:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
                
        except Exception as e:
            logger.error(f"Error in TTS loop: {e}", exc_info=True)
            self.error_occurred.emit(f"Erreur TTS : {str(e)}")
            
        finally:
            self.is_speaking_active = False
            self.speaking_stopped.emit()
            
    def is_speaking(self) -> bool:
        """Check if currently speaking"""
        return self.is_speaking_active
        
    def cleanup(self):
        """Cleanup resources"""
        logger.info("Cleaning up VoiceService...")
        
        # Stop listening
        self.stop_listening()
        
        # Stop speaking
        self.stop_speaking()
        
        # Cleanup TTS engine
        if self.tts_engine:
            try:
                self.tts_engine.stop()
            except:
                pass
                
        logger.info("VoiceService cleaned up")
        
    def __del__(self):
        """Destructor"""
        self.cleanup()
