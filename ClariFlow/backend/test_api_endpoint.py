#!/usr/bin/env python3
"""
Simple API test for the universal chat endpoint.
Tests the FastAPI endpoint directly.
"""

import requests

def test_api_endpoint():
    """Test the universal chat API endpoint."""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Universal Chat API Endpoint")
    print("=" * 50)
    
    # Test 1: Basic chat request
    print("\n📝 Test 1: Basic Chat Request")
    print("-" * 30)
    
    payload = {
        "query": "Hello, how are you?",
        "history": []
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat", json=payload)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Source: {data['source']}")
            print(f"✅ Used Context: {data['used_context']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Chat with history
    print("\n💬 Test 2: Chat with History")
    print("-" * 30)
    
    payload_with_history = {
        "query": "Can you elaborate on that?",
        "history": [
            "What is machine learning?",
            "Machine learning is a subset of AI that enables computers to learn from data."
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/api/chat", json=payload_with_history)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response: {data['response'][:100]}...")
            print(f"✅ Source: {data['source']}")
            print(f"✅ Used Context: {data['used_context']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 3: Get available documents
    print("\n📚 Test 3: Get Available Documents")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/api/documents")
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Documents: {data['documents']}")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Health check
    print("\n🏥 Test 4: Health Check")
    print("-" * 30)
    
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Server is healthy!")
        else:
            print(f"❌ Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    print("\n🎉 API Testing completed!")
    print("\n💡 To start the server, run: python main.py")

if __name__ == "__main__":
    test_api_endpoint() 