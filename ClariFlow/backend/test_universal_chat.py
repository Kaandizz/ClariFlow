#!/usr/bin/env python3
"""
Test script for universal chatbot functionality.
Tests both document-based and general chat scenarios.
"""

import asyncio
from app.services.chat_service import ChatService
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_universal_chat():
    """Test the universal chat functionality."""
    chat_service = ChatService()
    
    print("🧪 Testing Universal Chatbot Functionality")
    print("=" * 50)
    
    # Test 1: General chat without documents
    print("\n📝 Test 1: General Chat (No Documents)")
    print("-" * 30)
    
    query1 = "What is the capital of France?"
    history1 = ["Hello!", "Hi there! How can I help you today?"]
    
    try:
        result1 = await chat_service.chat(query=query1, history=history1)
        print(f"✅ Query: {query1}")
        print(f"✅ Response: {result1['response'][:100]}...")
        print(f"✅ Source: {result1['source']}")
        print(f"✅ Used Context: {result1['used_context']}")
        print(f"✅ Relevance Score: {result1['relevance_score']}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 2: Document-based chat (if documents exist)
    print("\n📄 Test 2: Document-Based Chat")
    print("-" * 30)
    
    available_docs = chat_service.get_available_documents()
    print(f"📚 Available documents: {available_docs}")
    
    if available_docs:
        query2 = "What are the main topics discussed in the document?"
        history2 = ["Can you help me understand this document?", "Of course! I'd be happy to help you understand the document."]
        
        try:
            result2 = await chat_service.chat(query=query2, history=history2)
            print(f"✅ Query: {query2}")
            print(f"✅ Response: {result2['response'][:100]}...")
            print(f"✅ Source: {result2['source']}")
            print(f"✅ Used Context: {result2['used_context']}")
            print(f"✅ Document ID: {result2['document_id']}")
            print(f"✅ Relevance Score: {result2['relevance_score']}")
            if result2['matched_chunks']:
                print(f"✅ Matched Chunks: {len(result2['matched_chunks'])} chunks found")
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    else:
        print("ℹ️  No documents available for document-based testing")
    
    # Test 3: Conversation flow
    print("\n💬 Test 3: Conversation Flow")
    print("-" * 30)
    
    conversation_history = [
        "Hello!",
        "Hi there! How can I help you today?",
        "I'm interested in learning about AI",
        "AI is a fascinating field! It involves creating intelligent machines that can perform tasks that typically require human intelligence. What specific aspect of AI interests you?"
    ]
    
    query3 = "Can you tell me more about machine learning?"
    
    try:
        result3 = await chat_service.chat(query=query3, history=conversation_history)
        print(f"✅ Query: {query3}")
        print(f"✅ Response: {result3['response'][:100]}...")
        print(f"✅ Source: {result3['source']}")
        print(f"✅ Used Context: {result3['used_context']}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    
    # Test 4: Edge cases
    print("\n🔍 Test 4: Edge Cases")
    print("-" * 30)
    
    # Empty query
    try:
        result4 = await chat_service.chat(query="", history=[])
        print(f"✅ Empty query handled: {result4['response'][:50]}...")
    except Exception as e:
        print(f"❌ Empty query error: {str(e)}")
    
    # Very long history
    long_history = ["Message " + str(i) for i in range(10)]
    try:
        result5 = await chat_service.chat(query="Test with long history", history=long_history)
        print(f"✅ Long history handled: {len(result5['response'])} chars")
    except Exception as e:
        print(f"❌ Long history error: {str(e)}")
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    asyncio.run(test_universal_chat()) 