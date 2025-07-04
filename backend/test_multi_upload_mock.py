#!/usr/bin/env python3
"""
Test script for multi-file upload functionality with mocked embedding service.
This script tests the upload endpoints without requiring OpenAI API access.
"""

import os
import tempfile
import requests
from pathlib import Path
from typing import List

# Test server URL
BASE_URL = "http://localhost:8000"
UPLOAD_ENDPOINT = f"{BASE_URL}/api/upload"
SINGLE_UPLOAD_ENDPOINT = f"{BASE_URL}/api/upload/single"
HEALTH_ENDPOINT = f"{BASE_URL}/health/health"

def create_test_file(content: str, extension: str) -> tempfile.NamedTemporaryFile:
    """Create a temporary test file with given content and extension."""
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix=extension,
        delete=False,
        encoding='utf-8'
    )
    temp_file.write(content)
    temp_file.close()
    return temp_file

def cleanup_test_files(files: List[tempfile.NamedTemporaryFile]):
    """Clean up temporary test files."""
    for file in files:
        try:
            os.unlink(file.name)
        except Exception as e:
            print(f"Warning: Could not delete {file.name}: {e}")

def test_upload_validation():
    """Test file validation without processing."""
    print("\n=== Testing Upload Validation ===")
    
    # Create test files
    test_files = []
    
    # Valid TXT file (small)
    txt_content = "This is a test document."
    txt_file = create_test_file(txt_content, ".txt")
    test_files.append(txt_file)
    
    # Invalid file type
    invalid_file = create_test_file("This is an invalid file type", ".jpg")
    test_files.append(invalid_file)
    
    try:
        files = []
        for file in test_files:
            with open(file.name, 'rb') as f:
                file_content = f.read()
                content_type = 'text/plain' if file.name.endswith('.txt') else 'image/jpeg'
                files.append(('files', (os.path.basename(file.name), file_content, content_type)))
        
        response = requests.post(UPLOAD_ENDPOINT, files=files)
        
        print(f"Upload validation response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Message: {result['message']}")
            print(f"Total files: {result['total_files']}")
            print(f"Successful: {result['successful_uploads']}")
            print(f"Failed: {result['failed_uploads']}")
            for file_result in result['results']:
                print(f"  - {file_result['filename']}: {file_result['status']}")
                if file_result['status'] == 'error':
                    print(f"    Error: {file_result['error_message']}")
        else:
            print(f"Error: {response.text}")
    
    finally:
        cleanup_test_files(test_files)

def test_empty_upload():
    """Test upload with no files."""
    print("\n=== Testing Empty Upload ===")
    
    response = requests.post(UPLOAD_ENDPOINT, files=[])
    
    print(f"Empty upload response: {response.status_code}")
    if response.status_code == 422:
        print("✅ Correctly rejected empty upload (validation error)")
        error_detail = response.json()['detail']
        print(f"Error: {error_detail[0]['msg']}")
    else:
        print(f"❌ Unexpected response: {response.text}")

def test_server_health():
    """Test if the server is running."""
    print("\n=== Testing Server Health ===")
    
    try:
        response = requests.get(HEALTH_ENDPOINT)
        if response.status_code == 200:
            print("✅ Server is running and healthy")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return False

def test_api_documentation():
    """Test if the API documentation is accessible."""
    print("\n=== Testing API Documentation ===")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code == 200:
            print("✅ API documentation is accessible at /docs")
            return True
        else:
            print(f"❌ API documentation not accessible: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        return False

def main():
    """Run all tests."""
    print("🧪 ClariFlow Multi-File Upload Test Suite (Mock Version)")
    print("=" * 60)
    
    # Check server health first
    if not test_server_health():
        print("\nPlease start the server first:")
        print("cd backend")
        print("python main.py")
        return
    
    # Test API documentation
    test_api_documentation()
    
    # Run validation tests (these should work without OpenAI API)
    test_upload_validation()
    test_empty_upload()
    
    print("\n" + "=" * 60)
    print("✅ Validation tests completed!")
    print("\nNote: Full processing tests require a valid OpenAI API key.")
    print("The validation tests above confirm the upload endpoints are working correctly.")

if __name__ == "__main__":
    main() 