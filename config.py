"""Configuration settings for the Chat Intelligence System"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{BASE_DIR / "chat_intelligence.db"}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SocketIO settings
    SOCKETIO_ASYNC_MODE = 'threading'
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"  # Change in production
    
    # ML Models settings
    EMOTION_MODEL = 'j-hartmann/emotion-english-distilroberta-base'
    SPACY_MODEL = 'en_core_web_sm'
    
    # Model optimization
    USE_ONNX = False  # Set to True after conversion
    MAX_MESSAGE_LENGTH = 500
    
    # Rate limiting
    RATE_LIMIT_MESSAGES = "10/minute"
    
    # Analytics settings
    ANALYTICS_UPDATE_INTERVAL = 2  # seconds
    MAX_RECENT_MESSAGES = 100
    
    # Logging
    LOG_LEVEL = 'INFO'
