"""ML Pipeline for NLP Analysis"""
import logging
from typing import Dict, List, Optional
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLPipeline:
    """Manages all ML models and provides unified analysis interface"""
    
    def __init__(self):
        self.emotion_model = None
        self.emotion_tokenizer = None
        self.ner_model = None
        self.sentiment_model = None
        self.sentiment_tokenizer = None
        self._models_loaded = False
        
    def load_models(self):
        """Load all ML models at startup"""
        try:
            logger.info("Loading ML models...")
            
            # 1. Load Emotion Detection Model (GoEmotions)
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            logger.info("Loading emotion detection model...")
            self.emotion_tokenizer = AutoTokenizer.from_pretrained(
                'j-hartmann/emotion-english-distilroberta-base'
            )
            self.emotion_model = AutoModelForSequenceClassification.from_pretrained(
                'j-hartmann/emotion-english-distilroberta-base'
            )
            self.emotion_labels = [
                'anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise'
            ]
            
            # 2. Load NER Model (spaCy)
            import spacy
            logger.info("Loading NER model...")
            try:
                self.ner_model = spacy.load('en_core_web_sm')
            except OSError:
                logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")
                self.ner_model = None
            
            # 3. Load Sentiment Model for Aspect Analysis
            logger.info("Loading sentiment model for aspect analysis...")
            self.sentiment_tokenizer = AutoTokenizer.from_pretrained(
                'distilbert-base-uncased-finetuned-sst-2-english'
            )
            self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(
                'distilbert-base-uncased-finetuned-sst-2-english'
            )
            
            self._models_loaded = True
            logger.info("✅ All models loaded successfully!")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            self._models_loaded = False
            
    def detect_emotion(self, text: str) -> Dict[str, any]:
        """Detect emotions in text using GoEmotions model"""
        if not self._models_loaded or self.emotion_model is None:
            return {'primary_emotion': 'neutral', 'scores': {}}
        
        try:
            import torch
            
            # Tokenize and run inference
            inputs = self.emotion_tokenizer(text, return_tensors='pt', truncation=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.emotion_model(**inputs)
                probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            # Get scores for all emotions
            scores = probs[0].tolist()
            emotion_scores = {label: float(score) for label, score in zip(self.emotion_labels, scores)}
            
            # Get primary emotion (highest score)
            primary_idx = np.argmax(scores)
            primary_emotion = self.emotion_labels[primary_idx]
            primary_score = scores[primary_idx]
            
            return {
                'primary_emotion': primary_emotion,
                'confidence': primary_score,
                'scores': emotion_scores
            }
            
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return {'primary_emotion': 'neutral', 'scores': {}}
    
    def extract_entities(self, text: str) -> List[Dict[str, any]]:
        """Extract named entities using spaCy"""
        if not self._models_loaded or self.ner_model is None:
            return []
        
        try:
            doc = self.ner_model(text)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char
                })
            
            return entities
            
        except Exception as e:
            logger.error(f"NER error: {e}")
            return []
    
    def analyze_aspect_sentiment(self, text: str, entities: List[Dict]) -> Dict[str, str]:
        """Analyze sentiment for each detected entity/aspect"""
        if not self._models_loaded or self.sentiment_model is None:
            return {}
        
        try:
            import torch
            
            aspect_sentiments = {}
            
            # For each entity, analyze sentiment in context
            for entity in entities:
                entity_text = entity['text']
                
                # Extract context around entity (simple window approach)
                start = max(0, entity['start'] - 50)
                end = min(len(text), entity['end'] + 50)
                context = text[start:end]
                
                # Run sentiment analysis
                inputs = self.sentiment_tokenizer(
                    context, 
                    return_tensors='pt', 
                    truncation=True, 
                    max_length=512
                )
                
                with torch.no_grad():
                    outputs = self.sentiment_model(**inputs)
                    probs = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
                # Labels: [negative, positive]
                negative_score = probs[0][0].item()
                positive_score = probs[0][1].item()
                
                # Determine sentiment
                if positive_score > 0.6:
                    sentiment = 'positive'
                elif negative_score > 0.6:
                    sentiment = 'negative'
                else:
                    sentiment = 'neutral'
                
                aspect_sentiments[entity_text] = sentiment
            
            return aspect_sentiments
            
        except Exception as e:
            logger.error(f"Aspect sentiment error: {e}")
            return {}
    
    def analyze_message(self, text: str) -> Dict[str, any]:
        """Run complete NLP analysis pipeline on a message"""
        if not self._models_loaded:
            logger.warning("Models not loaded, returning default values")
            return {
                'emotion': 'neutral',
                'emotion_scores': {},
                'entities': [],
                'aspect_sentiment': {}
            }
        
        try:
            # Run all analyses
            emotion_result = self.detect_emotion(text)
            entities = self.extract_entities(text)
            aspect_sentiment = self.analyze_aspect_sentiment(text, entities)
            
            return {
                'emotion': emotion_result['primary_emotion'],
                'emotion_scores': emotion_result['scores'],
                'entities': entities,
                'aspect_sentiment': aspect_sentiment
            }
            
        except Exception as e:
            logger.error(f"Message analysis error: {e}")
            return {
                'emotion': 'neutral',
                'emotion_scores': {},
                'entities': [],
                'aspect_sentiment': {}
            }

# Global ML pipeline instance
ml_pipeline = MLPipeline()
