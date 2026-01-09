

# VADER Sentiment Analysis Integration
#
# 1. No API key required. Just install vaderSentiment: pip install vaderSentiment
# 2. This script provides a function to analyze sentiment using VADER.


import os
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load .env file
load_dotenv()


analyzer = SentimentIntensityAnalyzer()

# Map Gemini sentiment to emoji/label
SENTIMENT_EMOJI = {
    'anger': '🤬',
    'disgust': '🤢',
    'fear': '😨',
    'joy': '😀',
    'neutral': '😐',
    'sadness': '😭',
    'surprise': '😲',
    # Add more as needed
}

def analyze_sentiment(text):
    vs = analyzer.polarity_scores(text)
    compound = vs['compound']
    # Map VADER compound score to categories
    if compound >= 0.5:
        category = 'joy'
    elif compound <= -0.5:
        category = 'sadness'
    elif compound > 0:
        category = 'neutral'  # Slightly positive, but not strong
    elif compound < 0:
        category = 'neutral'  # Slightly negative, but not strong
    else:
        category = 'neutral'
    emoji = SENTIMENT_EMOJI.get(category, '❓')
    return category, emoji
    sentiment = response.text.strip().lower()
    emoji = SENTIMENT_EMOJI.get(sentiment, '❓')
    return sentiment, emoji
