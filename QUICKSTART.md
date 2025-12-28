# Real-Time Chat Intelligence System - Quick Start Guide

## 📋 Prerequisites

- Python 3.8 or higher
- 8GB RAM minimum (for ML models)
- Modern web browser (Chrome, Firefox, Edge)

## 🚀 Quick Setup (Windows)

### Option 1: Automated Setup (Recommended)

1. **Double-click `setup.bat`** - This will automatically:

   - Create virtual environment
   - Install all dependencies
   - Download spaCy model
   - Initialize database

2. **Double-click `run.bat`** to start the application

3. **Open browser** and go to `http://localhost:5000`

### Option 2: Manual Setup

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download spaCy model
python -m spacy download en_core_web_sm

# 5. Initialize database
python init_db.py

# 6. Run the application
python app.py
```

## 📱 Using the Application

### 1. Join a Chat Room

- Enter your **username**
- Enter a **room name** (default: "general")
- Click **Join Chat**

### 2. Send Messages

- Type your message in the input box
- Press **Enter** or click **Send**
- Watch real-time NLP analysis appear below each message:
  - 😊 **Emotion**: joy, sadness, anger, fear, etc.
  - 🏷️ **Entities**: People, places, organizations
  - 💭 **Sentiment**: Positive/negative sentiment per entity

### 3. View Analytics Dashboard

- Click the **Analytics** tab
- View real-time charts:
  - **Emotion Distribution** (pie chart)
  - **Top Entities** (bar chart)
  - **Aspect Sentiment** (doughnut chart)
  - **Summary Statistics**
- Click **Refresh Analytics** to update manually

## 🎯 Example Messages to Try

Try these messages to see different NLP analyses:

```
"I love Python and machine learning! They are amazing."
→ Emotion: joy
→ Entities: Python (PRODUCT), machine learning (TECH)
→ Sentiment: Python (positive), machine learning (positive)

"The new iPhone is great but the price is too high."
→ Emotion: mixed (joy + anger)
→ Entities: iPhone (PRODUCT), price (MONEY)
→ Sentiment: iPhone (positive), price (negative)

"I'm worried about the weather in New York tomorrow."
→ Emotion: fear
→ Entities: New York (GPE), tomorrow (DATE)
→ Sentiment: weather (negative)
```

## 🔧 Troubleshooting

### Models Not Loading

**Problem**: "Models not loaded" message appears

**Solution**:

```bash
# Reinstall transformers and torch
pip install --upgrade transformers torch

# Download spaCy model again
python -m spacy download en_core_web_sm
```

### Port Already in Use

**Problem**: "Address already in use" error

**Solution**:

```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F

# Or change port in app.py (line at bottom):
socketio.run(app, port=5001)  # Use different port
```

### Database Errors

**Problem**: Database connection errors

**Solution**:

```bash
# Delete existing database
del chat_intelligence.db

# Reinitialize
python init_db.py
```

### Slow Performance

**Problem**: Messages take >5 seconds to process

**Solution**:

1. **Reduce model size**: In `ml_pipeline.py`, use smaller models
2. **Enable GPU**: Install CUDA and PyTorch with GPU support
3. **Optimize**: Convert models to ONNX (see Advanced section)

## 🎓 Understanding the NLP Features

### Emotion Detection (GoEmotions)

Detects 7 emotions from text:

- **joy**: happiness, excitement
- **sadness**: disappointment, grief
- **anger**: frustration, annoyance
- **fear**: worry, anxiety
- **surprise**: amazement, shock
- **disgust**: disapproval, dislike
- **neutral**: no strong emotion

### Named Entity Recognition (NER)

Identifies and categorizes entities:

- **PERSON**: People's names
- **ORG**: Organizations, companies
- **GPE**: Countries, cities
- **DATE**: Dates, time references
- **PRODUCT**: Products, brands
- **MONEY**: Monetary values
- **CARDINAL**: Numbers, quantities

### Aspect-Level Sentiment

Determines sentiment towards specific entities:

- **positive** 👍: Favorable opinion
- **negative** 👎: Unfavorable opinion
- **neutral** 😐: No clear sentiment

## 🚀 Advanced Features

### Use Multiple Rooms

Create different chat rooms for different topics:

```
Room: "tech-talk"  → Technical discussions
Room: "general"    → General chat
Room: "support"    → Customer support
```

### Export Chat History

```python
# In Python console
from app import app, db
from models import Message
import json

with app.app_context():
    messages = Message.query.all()
    data = [msg.to_dict() for msg in messages]

    with open('chat_export.json', 'w') as f:
        json.dump(data, f, indent=2)
```

### Performance Optimization (ONNX)

For 2-3x speedup, convert models to ONNX:

```bash
# Install ONNX dependencies
pip install onnx onnxruntime optimum

# Convert models (see documentation)
python -m optimum.exporters.onnx \
  --model j-hartmann/emotion-english-distilroberta-base \
  onnx_models/emotion/
```

Then update `config.py`:

```python
USE_ONNX = True
```

## 📊 Performance Benchmarks

### Expected Latency (CPU)

- Emotion Detection: 50-100ms
- NER: 10-20ms
- Aspect Sentiment: 30-50ms
- **Total**: ~150-250ms per message

### Expected Latency (GPU)

- Emotion Detection: 15-30ms
- NER: 5-10ms
- Aspect Sentiment: 10-20ms
- **Total**: ~30-80ms per message

### Concurrent Users

- **SQLite**: 20-50 users
- **PostgreSQL**: 100+ users (recommended for production)

## 🔒 Security Notes

**⚠️ Development Mode**

This is configured for **development only**. For production:

1. **Change SECRET_KEY** in `config.py`
2. **Use PostgreSQL** instead of SQLite
3. **Enable authentication** (add user login system)
4. **Use HTTPS** with SSL certificates
5. **Set CORS properly** in `app.py`
6. **Add rate limiting** (already configured but adjust limits)

## 📚 Tech Stack Details

- **Backend**: Flask 3.0 + Flask-SocketIO 5.3
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **ML Models**:
  - HuggingFace Transformers (DistilRoBERTa)
  - spaCy 3.7 (en_core_web_sm)
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **Charts**: Chart.js 4.4
- **UI**: Bootstrap 5.3

## 🤝 Support

For issues or questions:

1. Check the console output for error messages
2. Review the troubleshooting section above
3. Check the logs in terminal
4. Open an issue on GitHub (if applicable)

## 📝 Next Steps

Once you're comfortable with the basics:

1. ✅ Try different room names
2. ✅ Test with multiple browser windows (different users)
3. ✅ Experiment with various message types
4. ✅ Explore the analytics dashboard
5. ✅ Customize emotions and colors in CSS
6. ✅ Add new NLP features to the pipeline

---

**Enjoy exploring real-time NLP with your Chat Intelligence System! 🎉**
