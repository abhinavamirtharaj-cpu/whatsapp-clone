"""
UI.py
Flask server with real-time two-person messaging and sentiment analysis.

Features:
- Real-time WebSocket communication between two users
- Sentiment analysis on all messages
- Shared "LOCAL" chat room
- Message persistence with sender information

Run:
  pip install flask flask-socketio python-socketio textblob
  python UI.py

Access in browser: http://0.0.0.0:5000/
"""
import os
import sys
import json
from flask import Flask, send_from_directory, abort, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime

# Add parent directory to path to find other modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core_analysis.chat_service import process_user_message, get_history
from ui_io.storage import append_message

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_ROOT)
INTERFACE_JS_DIR = os.path.join(PROJECT_ROOT, 'interface_js')

# Disable default static file handling to allow custom routing for interface_js
app = Flask(__name__, static_folder=None)
app.config['SECRET_KEY'] = 'sean-chat-secret-key-2026'
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active users and their devices
active_sessions = {}


# Static file routes
@app.route('/')
def index():
    return send_from_directory(APP_ROOT, 'index.html')


@app.route('/<path:filename>')
def static_files(filename):
    # Check ui_io folder
    file_path = os.path.join(APP_ROOT, filename)
    if os.path.exists(file_path):
        return send_from_directory(APP_ROOT, filename)
   
    # Check interface_js folder (for script.js)
    js_path = os.path.join(INTERFACE_JS_DIR, filename)
    if os.path.exists(js_path):
        return send_from_directory(INTERFACE_JS_DIR, filename)
       
    abort(404)


# WebSocket Events for Real-time Communication
@socketio.on('join_chat')
def handle_join(data):
    """
    User joins the LOCAL chat room.
    Broadcasts join notification and sends chat history.
    """
    username = data.get('username', 'Anonymous')
    room = 'LOCAL'  # Common room name for both users
   
    join_room(room)
    active_sessions[request.sid] = {'username': username, 'room': room}
   
    print(f"[WebSocket] {username} joined room: {room}")
   
    # Notify others that user joined
    emit('user_joined', {
        'username': username,
        'message': f'{username} joined the chat'
    }, room=room, skip_sid=request.sid)
   
    # Send chat history to the newly joined user
    try:
        messages = get_history('LOCAL')
        # Convert history to format expected by frontend
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'sender': msg.get('sender', 'Unknown'),
                'text': msg.get('text', ''),
                'timestamp': msg.get('iso', datetime.now().isoformat()),
                'sentiment': {
                    'category': msg.get('sentiment_category', 'Neutral'),
                    'emoji': msg.get('sentiment_emoji', ''),
                    'color': msg.get('color_hex', '#9E9E9E'),
                    'polarity': msg.get('sentiment_polarity', 0)
                }
            })
       
        emit('chat_history', {'messages': formatted_messages})
    except Exception as e:
        print(f"[Error] Failed to load chat history: {str(e)}")
        emit('chat_history', {'messages': []})


@socketio.on('send_message')
def handle_message(data):
    """
    Process and broadcast message to all users in the room.
    Applies sentiment analysis before broadcasting.
    """
    try:
        session = active_sessions.get(request.sid)
        if not session:
            emit('error', {'message': 'Session not found. Please rejoin.'})
            return
       
        username = session['username']
        room = session['room']
        text = data.get('text', '').strip()
       
        if not text:
            return
       
        print(f"[WebSocket] Message from {username}: {text}")
       
        # Process message with sentiment analysis
        contact = {'id': 'LOCAL', 'name': room}
        result = process_user_message(text, contact)
       
        # Prepare message data with sender information
        now = datetime.now()
        message_with_sender = {
            'sender': username,
            'text': text,
            'timestamp': now.isoformat(),
            'sentiment': {
                'category': result['sentiment']['category'],
                'emoji': result['sentiment']['emoji'],
                'color': result['sentiment']['color'],
                'polarity': result['sentiment']['polarity_score']
            },
            'trend': result.get('trend', 'stable')
        }
       
        # Manually save with sender info (override process_user_message storage)
        from ui_io.storage import append_message_with_sender
        try:
            append_message_with_sender(contact, {
                'dir': 'sent',
                'iso': now.isoformat(),
                'date': now.strftime('%Y-%m-%d'),
                'time': now.strftime('%H:%M'),
                'text': text,
                'sender': username,
                'sentiment_polarity': result['sentiment']['polarity_score'],
                'sentiment_category': result['sentiment']['category'],
                'sentiment_emoji': result['sentiment']['emoji'],
                'color_hex': result['sentiment']['color']
            })
        except:
            pass  # Fallback if function doesn't exist yet
       
        # Broadcast to all users in room
        emit('new_message', message_with_sender, room=room)
       
    except Exception as e:
        print(f"[Error] Failed to process message: {str(e)}")
        emit('error', {'message': str(e)})


@socketio.on('disconnect')
def handle_disconnect():
    """
    User disconnected from the chat.
    """
    session = active_sessions.pop(request.sid, None)
    if session:
        print(f"[WebSocket] {session['username']} disconnected")
        emit('user_left', {
            'username': session['username'],
            'message': f"{session['username']} left the chat"
        }, room=session['room'])


# API Routes (legacy support)
@app.route('/api/history/<contact_id>', methods=['GET'])
def get_chat_history(contact_id):
    """
    Endpoint to retrieve chat history for a contact.
   
    Response JSON:
    {
        "success": true,
        "messages": [...]
    }
    """
    try:
        messages = get_history(contact_id)
        return jsonify({"success": True, "messages": messages}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  SEAN - Two-Person Real-time Chat with Sentiment Analysis")
    print("="*60)
    print("\n  Server starting on http://0.0.0.0:5000")
    print("  Open this URL on two devices to start chatting!")
    print("\n" + "="*60 + "\n")
   
    socketio.run(app, debug=True, port=5000, host='0.0.0.0')