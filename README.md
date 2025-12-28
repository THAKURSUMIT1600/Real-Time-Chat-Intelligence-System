# 🧠 Real-Time Chat Intelligence System

A real-time chat application with advanced NLP capabilities including **Emotion Detection**, **Named Entity Recognition (NER)**, and **Aspect-Level Sentiment Analysis**.

## 🌟 Features

- **Real-Time Chat**: WebSocket-based instant messaging
- **Emotion Detection**: 27 emotion categories using GoEmotions dataset
- **Named Entity Recognition**: Automatic extraction of people, places, organizations
- **Aspect-Level Sentiment**: Understand sentiment towards specific entities/aspects
- **Live Analytics Dashboard**: Real-time visualization of chat insights
- **Multi-Room Support**: Separate chat rooms with independent analytics

## 📊 Tech Stack

- **Backend**: Flask + Flask-SocketIO
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **ML Models**: HuggingFace Transformers, spaCy
- **Database**: SQLite (development) / PostgreSQL (production)
- **Charts**: Chart.js
- **Styling**: Bootstrap 5

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm
```

### 2. Initialize Database

```bash
python init_db.py
```

### 3. Run the Application

```bash
python app.py
```

Open your browser and navigate to `http://localhost:5000`

## 📁 Project Structure

```
chat-intelligence-system/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models.py             # Database models
├── ml_pipeline.py        # ML model integration
├── init_db.py            # Database initialization
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css    # Custom styles
│   └── js/
│       └── app.js       # Frontend JavaScript
└── templates/
    └── index.html       # Main chat interface
```

## 🎯 Usage

### Sending Messages

1. Enter your username
2. Select or create a chat room
3. Type your message and press Enter or click Send
4. Watch real-time NLP analysis appear below each message

### Analytics Dashboard

Click the "Analytics" tab to view:

- Emotion distribution (pie chart)
- Top mentioned entities (bar chart)
- Sentiment trends over time (line chart)
- Aspect-level sentiment breakdown

## 🔧 Configuration

Edit `config.py` to customize:

- Database path
- Model selection
- Rate limiting
- Analytics update frequency

## 📈 Performance

- **Message Processing**: 150-250ms per message
- **Concurrent Users**: 20-50 (SQLite), 100+ (PostgreSQL)
- **Models Memory**: ~800MB-1.2GB RAM

## 🎓 Datasets Used

- **GoEmotions** (Google Research): 58k Reddit comments, 27 emotions
- **TweetNERD**: NER for social media text
- **SemEval 2014**: Aspect-based sentiment analysis

## 🚀 Future Enhancements

- [ ] ONNX model optimization (2-3x speedup)
- [ ] PostgreSQL migration for production
- [ ] User authentication system
- [ ] Message history export
- [ ] Multi-language support
- [ ] Mobile responsive design improvements

## 📝 License

MIT License - Feel free to use for academic or commercial projects

## 🤝 Contributing

Contributions welcome! Please open an issue or submit a pull request.

## 📧 Contact

For questions or support, please open an issue on GitHub.
