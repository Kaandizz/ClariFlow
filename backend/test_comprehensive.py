#!/usr/bin/env python3
"""
Comprehensive test script for ClariFlow backend.
Tests all major functionality to ensure fixes work properly.
"""

import os
import sys
import asyncio
import requests
import json
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.core.database import engine, Base
from app.models import User, ChatSession, ChatMessage
from app.services.chat_service import ChatService
from app.services.document_processing import DocumentProcessor
from app.services.embedding import EmbeddingService

def test_configuration():
    """Test that configuration is loaded correctly."""
    print("🔧 Testing configuration...")
    
    try:
        # Test required settings
        assert settings.OPENAI_API_KEY, "OpenAI API key is required"
        assert settings.SECRET_KEY, "Secret key is required"
        assert settings.DATABASE_URL, "Database URL is required"
        assert settings.CHROMA_PERSIST_DIRECTORY, "ChromaDB directory is required"
        
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_database_connection():
    """Test database connection and table creation."""
    print("🗄️ Testing database connection...")
    
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_embedding_service():
    """Test embedding service initialization."""
    print("🧠 Testing embedding service...")
    
    try:
        embedding_service = EmbeddingService()
        print("✅ Embedding service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Embedding service error: {e}")
        return False

def test_document_processor():
    """Test document processor initialization."""
    print("📄 Testing document processor...")
    
    try:
        processor = DocumentProcessor()
        print("✅ Document processor initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Document processor error: {e}")
        return False

def test_chat_service():
    """Test chat service initialization."""
    print("💬 Testing chat service...")
    
    try:
        chat_service = ChatService()
        print("✅ Chat service initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Chat service error: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints are accessible."""
    print("🌐 Testing API endpoints...")
    
    base_url = "http://localhost:8000"
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health endpoint accessible")
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False
            
        # Test API documentation
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible")
        else:
            print(f"❌ API documentation returned {response.status_code}")
            return False
            
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server. Make sure the server is running.")
        return False
    except Exception as e:
        print(f"❌ API test error: {e}")
        return False

def test_file_upload_directory():
    """Test that upload directory exists and is writable."""
    print("📁 Testing upload directory...")
    
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Test write permission
        test_file = upload_dir / "test_write.txt"
        test_file.write_text("test")
        test_file.unlink()  # Clean up
        
        print("✅ Upload directory is writable")
        return True
    except Exception as e:
        print(f"❌ Upload directory error: {e}")
        return False

def test_chroma_directory():
    """Test that ChromaDB directory exists and is accessible."""
    print("🔍 Testing ChromaDB directory...")
    
    try:
        chroma_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
        chroma_dir.mkdir(exist_ok=True)
        
        print("✅ ChromaDB directory is accessible")
        return True
    except Exception as e:
        print(f"❌ ChromaDB directory error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting comprehensive ClariFlow backend tests...\n")
    
    tests = [
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("Embedding Service", test_embedding_service),
        ("Document Processor", test_document_processor),
        ("Chat Service", test_chat_service),
        ("Upload Directory", test_file_upload_directory),
        ("ChromaDB Directory", test_chroma_directory),
        ("API Endpoints", test_api_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print('='*50)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! ClariFlow backend is ready.")
        return True
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 