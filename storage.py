"""
storage.py - CSV-based message storage with sender tracking

Stores chat messages with sentiment data for two-person chat system.
Each message includes sender information to differentiate users.
"""
import csv
import os
from datetime import datetime

# Path to the CSV file
STORAGE_FILE = os.path.join(os.path.dirname(__file__), 'chat_history_global.csv')


def append_message(contact: dict, message: dict):
    """
    Append a single message to the CSV file with sender information.
   
    Args:
        contact (dict): Contact info with 'id' and 'name'
        message (dict): Message data including sender, text, sentiment
    """
    os.makedirs(os.path.dirname(STORAGE_FILE) or '.', exist_ok=True)
   
    file_exists = os.path.isfile(STORAGE_FILE)
   
    with open(STORAGE_FILE, 'a', newline='', encoding='utf-8') as f:
        fieldnames = [
            'timestamp', 'contact_id', 'sender', 'dir', 'iso',
            'date', 'time', 'text',
            'sentiment_polarity', 'sentiment_category',
            'sentiment_emoji', 'color_hex'
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
       
        if not file_exists:
            writer.writeheader()
       
        # Prepare row data
        now = datetime.now()
        row = {
            'timestamp': now.isoformat(),
            'contact_id': contact.get('id', 'LOCAL'),
            'sender': message.get('sender', 'Unknown'),
            'dir': message.get('dir', 'sent'),
            'iso': message.get('iso', now.isoformat()),
            'date': message.get('date', now.strftime('%Y-%m-%d')),
            'time': message.get('time', now.strftime('%H:%M')),
            'text': message.get('text', ''),
            'sentiment_polarity': message.get('sentiment_polarity', 0),
            'sentiment_category': message.get('sentiment_category', 'neutral'),
            'sentiment_emoji': message.get('sentiment_emoji', ''),
            'color_hex': message.get('color_hex', '#9E9E9E')
        }
       
        writer.writerow(row)


def append_message_with_sender(contact: dict, message: dict):
    """
    Alias for append_message with explicit sender support.
    Used by WebSocket handler.
    """
    append_message(contact, message)


def append_messages(contact: dict, messages: list):
    """
    Append multiple messages at once.
   
    Args:
        contact (dict): Contact info
        messages (list): List of message dicts
    """
    for message in messages:
        append_message(contact, message)


def get_history(contact_id: str) -> list:
    """
    Retrieve all messages for a specific contact/room.
   
    Args:
        contact_id (str): The contact/room ID (e.g., 'LOCAL')
       
    Returns:
        list: List of message dictionaries
    """
    if not os.path.isfile(STORAGE_FILE):
        return []
   
    messages = []
    with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['contact_id'] == contact_id:
                messages.append(row)
   
    return messages


def get_all_messages_for_analysis() -> list:
    """
    Retrieve all messages for sentiment trend analysis.
   
    Returns:
        list: All messages from CSV
    """
    if not os.path.isfile(STORAGE_FILE):
        return []
   
    messages = []
    with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        messages = list(reader)
   
    return messages


def get_csv_path() -> str:
    """
    Get the absolute path to the CSV storage file.
   
    Returns:
        str: Absolute path to chat_history_global.csv
    """
    return STORAGE_FILE


def clear_history(contact_id: str = None):
    """
    Clear chat history. If contact_id is provided, only clear that contact.
    Otherwise, clear entire file.
   
    Args:
        contact_id (str, optional): Specific contact to clear
    """
    if contact_id is None:
        # Clear entire file
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)
    else:
        # Clear specific contact
        if not os.path.isfile(STORAGE_FILE):
            return
       
        messages = []
        with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            messages = [row for row in reader if row['contact_id'] != contact_id]
       
        # Rewrite file without the deleted contact's messages
        with open(STORAGE_FILE, 'w', newline='', encoding='utf-8') as f:
            if messages:
                fieldnames = list(messages[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(messages)
