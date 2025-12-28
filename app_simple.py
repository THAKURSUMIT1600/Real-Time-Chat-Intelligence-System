"""Simple Flask app without ML models for quick testing"""
from flask import Flask, render_template
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('join')
def handle_join(data):
    room = data.get('room', 'general')
    join_room(room)
    emit('user_joined', {'username': data['username'], 'room': room}, room=room)
    emit('message_history', {'messages': []})

@socketio.on('send_message')
def handle_message(data):
    # Mock analysis (no real ML)
    response = {
        'id': 1,
        'username': data['username'],
        'room': data['room'],
        'text': data['text'],
        'timestamp': datetime.utcnow().isoformat(),
        'analysis': {
            'emotion': 'joy',
            'emotion_scores': {'joy': 0.8, 'neutral': 0.2},
            'entities': [],
            'aspect_sentiment': {}
        }
    }
    emit('new_message', response, room=data['room'])

@socketio.on('get_analytics')
def handle_analytics(data):
    emit('analytics_update', {
        'room': data['room'],
        'message_count': 0,
        'emotion_distribution': {'joy': 1},
        'top_entities': [],
        'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
        'timestamp': datetime.utcnow().isoformat()
    })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 SIMPLE MODE - No ML Models")
    print("="*50)
    print("Open: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*50 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
