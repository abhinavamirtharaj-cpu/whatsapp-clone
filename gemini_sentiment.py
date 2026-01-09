# Gemini Sentiment Analysis Integration
#
# 1. Get a Gemini API key from Google AI Studio (https://aistudio.google.com/)
# 2. Set the key as an environment variable: export GEMINI_API_KEY=your-key
# 3. Install the required package: pip install google-genai
#
# This script provides a function to analyze sentiment using Gemini.


import os
from dotenv import load_dotenv
import google.genai as genai

# Load .env file
load_dotenv()
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise RuntimeError('GEMINI_API_KEY environment variable not set.')

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
    prompt = f"""
Classify the sentiment of the following message into one of these categories: anger, disgust, fear, joy, neutral, sadness, surprise. Respond with only the category name.

Message: {text}
"""
    model = genai.GenerativeModel('gemini-pro', api_key=GEMINI_API_KEY)
    response = model.generate_content([prompt])
    category = response.candidates[0].content.parts[0].text.strip().lower()
    emoji = SENTIMENT_EMOJI.get(category, '❓')
    return category, emoji
    sentiment = response.text.strip().lower()
    emoji = SENTIMENT_EMOJI.get(sentiment, '❓')
    return sentiment, emoji
