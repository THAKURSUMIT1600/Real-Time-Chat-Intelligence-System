"""Database models for Chat Intelligence System"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

class Message(db.Model):
    """Chat message with NLP analysis results"""
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    room = db.Column(db.String(50), nullable=False, default='general')
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # NLP Analysis Results (stored as JSON)
    emotion = db.Column(db.String(50))  # Primary emotion
    emotion_scores = db.Column(db.Text)  # JSON: all emotion probabilities
    entities = db.Column(db.Text)  # JSON: list of {text, label, start, end}
    aspect_sentiment = db.Column(db.Text)  # JSON: {aspect: sentiment}
    
    def __repr__(self):
        return f'<Message {self.id}: {self.username} in {self.room}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'room': self.room,
            'text': self.text,
            'timestamp': self.timestamp.isoformat(),
            'emotion': self.emotion,
            'emotion_scores': json.loads(self.emotion_scores) if self.emotion_scores else {},
            'entities': json.loads(self.entities) if self.entities else [],
            'aspect_sentiment': json.loads(self.aspect_sentiment) if self.aspect_sentiment else {}
        }

class User(db.Model):
    """User information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    message_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<User {self.username}>'

class AnalyticsSummary(db.Model):
    """Aggregated analytics for efficient dashboard queries"""
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    room = db.Column(db.String(50), nullable=False)
    emotion = db.Column(db.String(50))
    entity = db.Column(db.String(100))
    aspect = db.Column(db.String(100))
    sentiment = db.Column(db.String(20))
    count = db.Column(db.Integer, default=1)
    timestamp_bucket = db.Column(db.DateTime, nullable=False)  # Hourly buckets
    
    def __repr__(self):
        return f'<Analytics {self.room}: {self.emotion or self.entity}>'
