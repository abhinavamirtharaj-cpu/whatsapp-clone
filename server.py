from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
from collections import defaultdict
import os
from vader_sentiment import analyze_sentiment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}
user_public_keys = {}

@socketio.on('decrypted_message')
def handle_decrypted_message(data):
    # data: {text, originalUser}
    text = data['text']
    user = data.get('originalUser', 'unknown')
    try:
        sentiment, emoji = analyze_sentiment(text)
    except Exception as e:
        sentiment, emoji = 'unknown', '❓'
    # Broadcast only sentiment result (not the message)
    emit('sentiment_result', {
        'user': user,
        'sentiment': sentiment,
        'emoji': emoji
    }, broadcast=True)
from collections import defaultdict
import os
from vader_sentiment import analyze_sentiment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

users = {}
user_public_keys = {}

@app.route('/')
def index():
    return app.send_static_file('chat.html')

@socketio.on('join')
def on_join(data):
    username = data['username']
    public_key = data.get('publicKey')
    users[request.sid] = username
    if public_key:
        user_public_keys[username] = public_key
    emit('status', {'msg': f'{username} joined ✅'}, broadcast=True)
    emit('users', list(users.values()), broadcast=True)
    emit('user_public_keys', user_public_keys, broadcast=True)

@socketio.on('message')
def handle_message(data):
    username = users[request.sid]
    if data.get('encrypted'):
        # Broadcast encrypted payload as-is
        emit('message', {
            'user': username,
            'encrypted': True,
            'ciphertext': data['ciphertext'],
            'iv': data['iv'],
            'encryptedKeys': data['encryptedKeys']
        }, broadcast=True)
    else:
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
        user_public_keys.pop(username, None)
        emit('status', {'msg': f'{username} left 👋'}, broadcast=True)
        emit('user_public_keys', user_public_keys, broadcast=True)

if __name__ == '__main__':
    print("🌐 LOCAL: http://localhost:5000")
    try:
           print(" * Server running on http://localhost:5000 (or your public IP)")
    except:
           print(f"Error starting server: {e}")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
