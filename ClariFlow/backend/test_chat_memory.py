#!/usr/bin/env python3
"""
Test script for ClariFlow Chat Memory and Session Management
Tests all endpoints and functionality for chat sessions and message history.
"""

import requests
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_create_session():
    """Test creating a new chat session"""
    print("🔍 Testing session creation...")
    
    # Test creating session with default title
    response = requests.post(f"{API_BASE}/sessions", json={})
    print(f"Create session (default): {response.status_code}")
    if response.status_code == 200:
        session_data = response.json()
        print(f"Session created: {session_data}")
        session_id = session_data['id']
    else:
        print(f"Error: {response.text}")
        return None
    
    # Test creating session with custom title
    response = requests.post(f"{API_BASE}/sessions", json={"title": "Test Session"})
    print(f"Create session (custom): {response.status_code}")
    if response.status_code == 200:
        session_data = response.json()
        print(f"Session created: {session_data}")
    
    print()
    return session_id

def test_chat_with_session(session_id):
    """Test chat functionality with session"""
    print("🔍 Testing chat with session...")
    
    # Test first message (should auto-generate title)
    chat_data = {
        "query": "Hello, this is my first message in this session. Can you help me with document analysis?",
        "session_id": session_id
    }
    
    response = requests.post(f"{API_BASE}/chat", json=chat_data)
    print(f"First chat message: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['response'][:100]}...")
        print(f"Session ID: {result['session_id']}")
        print(f"Source: {result['source']}")
    else:
        print(f"Error: {response.text}")
    
    # Test second message
    chat_data = {
        "query": "What documents do you have available?",
        "session_id": session_id
    }
    
    response = requests.post(f"{API_BASE}/chat", json=chat_data)
    print(f"Second chat message: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['response'][:100]}...")
    else:
        print(f"Error: {response.text}")
    
    print()

def test_chat_without_session():
    """Test chat functionality without session (should create new session)"""
    print("🔍 Testing chat without session...")
    
    chat_data = {
        "query": "This is a new conversation without a session ID"
    }
    
    response = requests.post(f"{API_BASE}/chat", json=chat_data)
    print(f"Chat without session: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result['response'][:100]}...")
        print(f"New Session ID: {result['session_id']}")
        return result['session_id']
    else:
        print(f"Error: {response.text}")
        return None

def test_get_sessions():
    """Test getting all sessions"""
    print("🔍 Testing get all sessions...")
    
    response = requests.get(f"{API_BASE}/sessions")
    print(f"Get sessions: {response.status_code}")
    if response.status_code == 200:
        sessions = response.json()
        print(f"Found {len(sessions)} sessions:")
        for session in sessions:
            print(f"  - {session['title']} (ID: {session['id'][:8]}..., Messages: {session['message_count']})")
        return sessions
    else:
        print(f"Error: {response.text}")
        return []

def test_get_session_messages(session_id):
    """Test getting messages from a specific session"""
    print("🔍 Testing get session messages...")
    
    response = requests.get(f"{API_BASE}/sessions/{session_id}")
    print(f"Get session messages: {response.status_code}")
    if response.status_code == 200:
        messages = response.json()
        print(f"Found {len(messages)} messages:")
        for i, message in enumerate(messages, 1):
            print(f"  {i}. [{message['role']}] {message['content'][:50]}...")
        return messages
    else:
        print(f"Error: {response.text}")
        return []

def test_update_session_title(session_id):
    """Test updating session title"""
    print("🔍 Testing update session title...")
    
    new_title = f"Updated Session - {datetime.now().strftime('%H:%M:%S')}"
    update_data = {"title": new_title}
    
    response = requests.put(f"{API_BASE}/sessions/{session_id}", json=update_data)
    print(f"Update session title: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Updated title: {result['title']}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_delete_session(session_id):
    """Test deleting a session"""
    print("🔍 Testing delete session...")
    
    response = requests.delete(f"{API_BASE}/sessions/{session_id}")
    print(f"Delete session: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Delete result: {result}")
        return True
    else:
        print(f"Error: {response.text}")
        return False

def test_documents_endpoint():
    """Test getting available documents"""
    print("🔍 Testing documents endpoint...")
    
    response = requests.get(f"{API_BASE}/documents")
    print(f"Get documents: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Available documents: {result}")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("🚀 Starting ClariFlow Chat Memory Tests")
    print("=" * 50)
    
    # Test health
    test_health()
    
    # Test documents endpoint
    test_documents_endpoint()
    
    # Test session management
    session_id = test_create_session()
    
    if session_id:
        # Test chat with session
        test_chat_with_session(session_id)
        
        # Test getting session messages
        test_get_session_messages(session_id)
        
        # Test updating session title
        test_update_session_title(session_id)
    
    # Test chat without session
    new_session_id = test_chat_without_session()
    
    # Test getting all sessions
    sessions = test_get_sessions()
    
    # Test getting messages from new session
    if new_session_id:
        test_get_session_messages(new_session_id)
    
    # Test deleting a session (use the new session to avoid breaking the main one)
    if new_session_id:
        test_delete_session(new_session_id)
    
    print("✅ Chat Memory Tests Completed!")
    print("=" * 50)

if __name__ == "__main__":
    main() 