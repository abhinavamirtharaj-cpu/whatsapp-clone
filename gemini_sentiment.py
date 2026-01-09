
# OpenAI Sentiment Analysis Integration
#
# 1. Get an OpenAI API key from https://platform.openai.com/
# 2. Set the key as an environment variable: export OPENAI_API_KEY=your-key
# 3. Install the required package: pip install openai
#
# This script provides a function to analyze sentiment using OpenAI.


import os
from dotenv import load_dotenv
import openai

# Load .env file
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    raise RuntimeError('OPENAI_API_KEY environment variable not set.')

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
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            api_key=OPENAI_API_KEY
        )
        category = response.choices[0].message['content'].strip().lower()
    except Exception as e:
        print("Error extracting sentiment:", e)
        category = 'unknown'
    emoji = SENTIMENT_EMOJI.get(category, '❓')
    return category, emoji
    sentiment = response.text.strip().lower()
    emoji = SENTIMENT_EMOJI.get(sentiment, '❓')
    return sentiment, emoji
