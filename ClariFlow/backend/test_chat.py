#!/usr/bin/env python3
"""
Test script for the enhanced ClariFlow chat endpoint.
Tests both document-based and general chat functionality.
"""

import requests

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def test_general_chat():
    """Test general chat functionality."""
    print("\n🤖 Testing general chat...")
    
    test_queries = [
        "What is the capital of France?",
        "Explain quantum computing in simple terms",
        "Write a short poem about technology"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing query: '{query}'")
        try:
            payload = {"query": query}
            response = requests.post(f"{BASE_URL}/api/chat", json=payload)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data['response'][:100]}...")
                print(f"   Source: {data['source']}")
                print(f"   Timestamp: {data['timestamp']}")
            else:
                print(f"❌ Failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

def test_documents_endpoint():
    """Test the documents endpoint."""
    print("\n📄 Testing documents endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/documents")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Available documents: {data['documents']}")
            return data['documents']
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"❌ Error: {e}")
        return []

def test_invalid_request():
    """Test invalid request handling."""
    print("\n🚫 Testing invalid request handling...")
    
    # Test empty query
    try:
        payload = {"query": ""}
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 400:
            print("✅ Empty query properly rejected")
        else:
            print(f"❌ Empty query not rejected: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test missing query field
    try:
        payload = {"message": "This should fail"}
        response = requests.post(f"{BASE_URL}/api/chat", json=payload)
        if response.status_code == 422:  # Validation error
            print("✅ Missing query field properly rejected")
        else:
            print(f"❌ Missing query field not rejected: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting ClariFlow Chat API Tests")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("❌ Health check failed, stopping tests")
        return
    
    # Test documents endpoint
    documents = test_documents_endpoint()
    
    # Test general chat
    test_general_chat()
    
    # Test invalid requests
    test_invalid_request()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    
    if documents:
        print(f"📚 {len(documents)} document(s) available for testing")
        print("💡 Try uploading a document to test document-based chat!")
    else:
        print("📚 No documents available - general chat mode only")

if __name__ == "__main__":
    main() 