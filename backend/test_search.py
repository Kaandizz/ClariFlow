#!/usr/bin/env python3
"""
Test script for the search functionality.
This script tests the search endpoints to ensure they work correctly.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000/api"

def test_search_endpoint():
    """Test the search endpoint with a sample query."""
    print("Testing search endpoint...")
    
    # Test data
    search_data = {
        "query": "What is the main topic of the document?",
        "top_k": 5
    }
    
    try:
        response = requests.post(f"{BASE_URL}/search", json=search_data)
        
        if response.status_code == 200:
            results = response.json()
            print(f"✅ Search successful!")
            print(f"Query: {results['query']}")
            print(f"Total results: {results['total_results']}")
            
            for i, result in enumerate(results['results'], 1):
                print(f"\nResult {i}:")
                print(f"  Text: {result['text'][:100]}...")
                print(f"  Score: {result['score']}")
                print(f"  Source: {result['source_file']}")
                if result.get('page_number'):
                    print(f"  Page: {result['page_number']}")
        else:
            print(f"❌ Search failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the backend is running.")
    except Exception as e:
        print(f"❌ Error during search test: {e}")

def test_documents_endpoint():
    """Test the documents endpoint to get available documents."""
    print("\nTesting documents endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/documents")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Documents endpoint successful!")
            print(f"Total documents: {data.get('total_documents', 0)}")
            
            documents = data.get('documents', [])
            for doc in documents:
                print(f"  - {doc['source_file']} (ID: {doc['document_id']}, Chunks: {doc['chunk_count']})")
        else:
            print(f"❌ Documents endpoint failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the server. Make sure the backend is running.")
    except Exception as e:
        print(f"❌ Error during documents test: {e}")

def test_search_with_file_id():
    """Test search with a specific file ID."""
    print("\nTesting search with file ID...")
    
    # First get available documents
    try:
        response = requests.get(f"{BASE_URL}/documents")
        if response.status_code == 200:
            data = response.json()
            documents = data.get('documents', [])
            if documents:
                # Use the first available document
                file_id = documents[0]['document_id']
                
                search_data = {
                    "query": "test query",
                    "file_id": file_id,
                    "top_k": 3
                }
                
                response = requests.post(f"{BASE_URL}/search", json=search_data)
                
                if response.status_code == 200:
                    results = response.json()
                    print(f"✅ Search with file ID successful!")
                    print(f"Query: {results['query']}")
                    print(f"Results: {results['total_results']}")
                else:
                    print(f"❌ Search with file ID failed: {response.text}")
            else:
                print("ℹ️  No documents available for testing")
        else:
            print(f"❌ Could not get documents: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during file ID search test: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting ClariFlow Search Tests")
    print("=" * 50)
    
    # Wait a moment for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Run tests
    test_documents_endpoint()
    test_search_endpoint()
    test_search_with_file_id()
    
    print("\n" + "=" * 50)
    print("✅ Search tests completed!")

if __name__ == "__main__":
    main() 