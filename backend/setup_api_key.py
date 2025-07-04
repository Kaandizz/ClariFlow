#!/usr/bin/env python3
"""
Simple script to help set up the OpenAI API key for ClariFlow.
"""

import os
from pathlib import Path

def setup_api_key():
    """Help user set up their OpenAI API key."""
    print("🔑 ClariFlow API Key Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_path = Path(".env")
    
    if env_path.exists():
        print("📁 Found existing .env file")
        
        # Read current content
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Check if API key is already set
        if "OPENAI_API_KEY=" in content:
            print("⚠️  OpenAI API key is already set in .env file")
            print("   Current key appears to be invalid (causing 401 errors)")
            print()
            
            # Ask if user wants to update it
            update = input("Do you want to update the API key? (y/n): ").lower().strip()
            if update != 'y':
                print("❌ API key not updated. Please update it manually.")
                return
    else:
        print("📁 Creating new .env file")
    
    print()
    print("🔑 To get your OpenAI API key:")
    print("   1. Go to https://platform.openai.com/account/api-keys")
    print("   2. Click 'Create new secret key'")
    print("   3. Copy the key (starts with 'sk-')")
    print()
    
    # Get API key from user
    api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Setup cancelled.")
        return
    
    if not api_key.startswith('sk-'):
        print("⚠️  Warning: API key should start with 'sk-'")
        continue_anyway = input("Continue anyway? (y/n): ").lower().strip()
        if continue_anyway != 'y':
            print("❌ Setup cancelled.")
            return
    
    # Create or update .env file
    env_content = f"""LOG_LEVEL=INFO
OPENAI_API_KEY={api_key}
CHROMA_PERSIST_DIRECTORY=chroma_db
"""
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print()
    print("✅ API key saved to .env file!")
    print("🔄 Please restart your backend server for changes to take effect.")
    print()
    print("To restart the server:")
    print("   1. Stop the current server (Ctrl+C)")
    print("   2. Run: python main.py")

def test_api_key():
    """Test if the API key is working."""
    print("\n🧪 Testing API key...")
    
    try:
        from app.core.config import settings
        from app.services.embedding import EmbeddingService
        
        # Try to create embeddings
        embedding_service = EmbeddingService()
        test_embeddings = embedding_service.create_embeddings(["test"])
        
        if test_embeddings and len(test_embeddings) > 0:
            print("✅ API key is working correctly!")
            return True
        else:
            print("❌ API key test failed - no embeddings returned")
            return False
            
    except Exception as e:
        print(f"❌ API key test failed: {e}")
        return False

if __name__ == "__main__":
    setup_api_key()
    
    # Test the API key if user wants
    test = input("\nDo you want to test the API key? (y/n): ").lower().strip()
    if test == 'y':
        test_api_key() 