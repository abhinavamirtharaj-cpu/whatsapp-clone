
from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
from collections import defaultdict
import os
from gemini_sentiment import analyze_sentiment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}

@app.route('/')
def index():
    return app.send_static_file('chat.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    users[request.sid] = username
    emit('status', {'msg': f'{username} joined ✅'}, broadcast=True)
    emit('users', list(users.values()), broadcast=True)

@socketio.on('message')
def handle_message(data):
    username = users[request.sid]
    text = data['text']
    try:
        sentiment, emoji = analyze_sentiment(text)
    except Exception as e:
        sentiment, emoji = 'unknown', '❓'
    emit('message', {
        'user': username,
        'text': text,
        'sentiment': sentiment,
        'emoji': emoji
    }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        username = users.pop(request.sid)
        emit('status', {'msg': f'{username} left 👋'}, broadcast=True)

if __name__ == '__main__':
    print("🌐 LOCAL: http://localhost:5000")
    try:
        from pyngrok import ngrok
        public_url = ngrok.connect(5000)
        print(f"🌍 PUBLIC: {public_url}")
    except:
        print("❌ pip install pyngrok for public URL")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
