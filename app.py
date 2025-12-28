"""Flask application with SocketIO for real-time chat and NLP analysis"""
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import json
import logging

from config import Config
from models import db, Message, User, AnalyticsSummary
from ml_pipeline import ml_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
CORS(app)
db.init_app(app)
socketio = SocketIO(
    app, 
    cors_allowed_origins="*",
    async_mode='threading',
    logger=True,
    engineio_logger=False
)

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Store active users per room
active_users = {}

@app.route('/')
def index():
    """Serve the main chat interface"""
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'models_loaded': ml_pipeline._models_loaded,
        'timestamp': datetime.utcnow().isoformat()
    }

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f'Client connected: {request.sid}')
    emit('connection_response', {'status': 'connected', 'sid': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')
    
    # Remove user from active users
    for room, users in active_users.items():
        if request.sid in users:
            username = users[request.sid]
            del users[request.sid]
            emit('user_left', {'username': username, 'room': room}, room=room)

@socketio.on('join')
def handle_join(data):
    """Handle user joining a room"""
    username = data.get('username', 'Anonymous')
    room = data.get('room', 'general')
    
    join_room(room)
    
    # Track active user
    if room not in active_users:
        active_users[room] = {}
    active_users[room][request.sid] = username
    
    # Update user in database
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username)
        db.session.add(user)
    user.last_active = datetime.utcnow()
    db.session.commit()
    
    logger.info(f'{username} joined room: {room}')
    
    # Notify others in the room
    emit('user_joined', {
        'username': username,
        'room': room,
        'timestamp': datetime.utcnow().isoformat()
    }, room=room)
    
    # Send recent messages to the user
    recent_messages = Message.query.filter_by(room=room)\
        .order_by(Message.timestamp.desc())\
        .limit(50)\
        .all()
    
    emit('message_history', {
        'messages': [msg.to_dict() for msg in reversed(recent_messages)]
    })

@socketio.on('leave')
def handle_leave(data):
    """Handle user leaving a room"""
    username = data.get('username')
    room = data.get('room', 'general')
    
    leave_room(room)
    
    # Remove from active users
    if room in active_users and request.sid in active_users[room]:
        del active_users[room][request.sid]
    
    logger.info(f'{username} left room: {room}')
    emit('user_left', {'username': username, 'room': room}, room=room)

@socketio.on('send_message')
@limiter.limit("10/minute")
def handle_message(data):
    """Handle incoming chat message with NLP analysis"""
    try:
        username = data.get('username', 'Anonymous')
        room = data.get('room', 'general')
        text = data.get('text', '').strip()
        
        if not text:
            emit('error', {'message': 'Empty message'})
            return
        
        if len(text) > Config.MAX_MESSAGE_LENGTH:
            emit('error', {'message': f'Message too long (max {Config.MAX_MESSAGE_LENGTH} chars)'})
            return
        
        logger.info(f'Message from {username} in {room}: {text[:50]}...')
        
        # Run NLP analysis
        analysis = ml_pipeline.analyze_message(text)
        
        # Save to database
        message = Message(
            username=username,
            room=room,
            text=text,
            emotion=analysis['emotion'],
            emotion_scores=json.dumps(analysis['emotion_scores']),
            entities=json.dumps(analysis['entities']),
            aspect_sentiment=json.dumps(analysis['aspect_sentiment'])
        )
        db.session.add(message)
        
        # Update user message count
        user = User.query.filter_by(username=username).first()
        if user:
            user.message_count += 1
            user.last_active = datetime.utcnow()
        
        db.session.commit()
        
        # Prepare response
        response = {
            'id': message.id,
            'username': username,
            'room': room,
            'text': text,
            'timestamp': message.timestamp.isoformat(),
            'analysis': analysis
        }
        
        # Broadcast to room
        emit('new_message', response, room=room)
        
        # Update analytics in background (simplified)
        update_analytics(room, analysis)
        
        logger.info(f'✅ Message processed - Emotion: {analysis["emotion"]}, Entities: {len(analysis["entities"])}')
        
    except Exception as e:
        logger.error(f'Error handling message: {e}', exc_info=True)
        emit('error', {'message': 'Failed to process message'})

@socketio.on('get_analytics')
def handle_get_analytics(data):
    """Get analytics data for dashboard"""
    try:
        room = data.get('room', 'general')
        
        # Get recent messages for analysis
        messages = Message.query.filter_by(room=room)\
            .order_by(Message.timestamp.desc())\
            .limit(Config.MAX_RECENT_MESSAGES)\
            .all()
        
        # Aggregate emotion data
        emotion_counts = {}
        entity_counts = {}
        aspect_sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        
        for msg in messages:
            # Emotion counts
            if msg.emotion:
                emotion_counts[msg.emotion] = emotion_counts.get(msg.emotion, 0) + 1
            
            # Entity counts
            if msg.entities:
                entities = json.loads(msg.entities)
                for entity in entities:
                    entity_text = entity['text']
                    entity_counts[entity_text] = entity_counts.get(entity_text, 0) + 1
            
            # Aspect sentiment counts
            if msg.aspect_sentiment:
                aspects = json.loads(msg.aspect_sentiment)
                for aspect, sentiment in aspects.items():
                    aspect_sentiments[sentiment] = aspect_sentiments.get(sentiment, 0) + 1
        
        # Get top entities
        top_entities = sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Prepare analytics response
        analytics = {
            'room': room,
            'message_count': len(messages),
            'emotion_distribution': emotion_counts,
            'top_entities': [{'entity': e[0], 'count': e[1]} for e in top_entities],
            'sentiment_distribution': aspect_sentiments,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        emit('analytics_update', analytics)
        
    except Exception as e:
        logger.error(f'Error getting analytics: {e}', exc_info=True)
        emit('error', {'message': 'Failed to get analytics'})

def update_analytics(room, analysis):
    """Update analytics summaries (simplified version)"""
    try:
        # This would typically be done in a background task
        # For now, keeping it simple without celery/redis
        pass
    except Exception as e:
        logger.error(f'Error updating analytics: {e}')

@app.before_request
def before_first_request():
    """Initialize app before first request"""
    pass

def init_app():
    """Initialize the application"""
    with app.app_context():
        # Create tables
        db.create_all()
        logger.info("✅ Database tables created")
        
        # Load ML models
        logger.info("Loading ML models (this may take a minute)...")
        ml_pipeline.load_models()
        
        if ml_pipeline._models_loaded:
            logger.info("✅ All systems ready!")
        else:
            logger.warning("⚠️ Models not loaded - app will run with limited functionality")

if __name__ == '__main__':
    # Initialize app
    init_app()
     import os
    port = int(os.environ.get('PORT', 5000))
    # Run with SocketIO
    logger.info("🚀 Starting Chat Intelligence System...")
    logger.info("📱 Open http://localhost:5000 in your browser")
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to prevent loading models twice
    )
