#!/usr/bin/env python3
"""
Example script demonstrating how to use ClariFlow's search functionality.
This script shows how to interact with the search API endpoints.
"""

import requests
import json
from typing import Dict, List, Optional

class ClariFlowSearchClient:
    """Client for interacting with ClariFlow's search API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api"
    
    def search_documents(self, query: str, file_id: Optional[str] = None, top_k: int = 5) -> Dict:
        """
        Search for documents using a query.
        
        Args:
            query: The search query
            file_id: Optional document ID to search within
            top_k: Number of results to return
            
        Returns:
            Search results dictionary
        """
        url = f"{self.api_base}/search"
        payload = {
            "query": query,
            "top_k": top_k
        }
        
        if file_id:
            payload["file_id"] = file_id
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_available_documents(self) -> Dict:
        """
        Get list of available documents.
        
        Returns:
            Dictionary containing available documents
        """
        url = f"{self.api_base}/documents"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def search_and_display(self, query: str, file_id: Optional[str] = None, top_k: int = 5):
        """
        Search and display results in a formatted way.
        
        Args:
            query: The search query
            file_id: Optional document ID
            top_k: Number of results to display
        """
        print(f"🔍 Searching for: '{query}'")
        if file_id:
            print(f"📁 Within document: {file_id}")
        print("-" * 60)
        
        try:
            results = self.search_documents(query, file_id, top_k)
            
            print(f"✅ Found {results['total_results']} results")
            print()
            
            for i, result in enumerate(results['results'], 1):
                print(f"Result {i}:")
                print(f"  📄 Source: {result['source_file']}")
                print(f"  📊 Score: {result['score']}")
                if result.get('page_number'):
                    print(f"  📖 Page: {result['page_number']}")
                if result.get('chunk_index'):
                    print(f"  🔢 Chunk: {result['chunk_index']}")
                print(f"  📝 Text: {result['text'][:150]}...")
                print()
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def main():
    """Main function demonstrating search functionality."""
    client = ClariFlowSearchClient()
    
    print("🚀 ClariFlow Search Example")
    print("=" * 60)
    
    # First, let's see what documents are available
    print("📚 Available Documents:")
    try:
        documents = client.get_available_documents()
        if documents['total_documents'] > 0:
            for doc in documents['documents']:
                print(f"  - {doc['source_file']} (ID: {doc['document_id']}, Chunks: {doc['chunk_count']})")
        else:
            print("  No documents available. Please upload some documents first.")
        print()
    except Exception as e:
        print(f"  ❌ Error getting documents: {e}")
        print()
    
    # Example searches
    example_searches = [
        "What is the main topic?",
        "What are the key features?",
        "How does it work?",
        "What are the requirements?"
    ]
    
    for query in example_searches:
        client.search_and_display(query, top_k=3)
        print("=" * 60)
    
    # Example of searching within a specific document
    if documents['total_documents'] > 0:
        file_id = documents['documents'][0]['document_id']
        print(f"🔍 Searching within specific document: {documents['documents'][0]['source_file']}")
        client.search_and_display("important information", file_id=file_id, top_k=2)
        print("=" * 60)

if __name__ == "__main__":
    main() 