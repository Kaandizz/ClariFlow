#!/usr/bin/env python3
"""
Test script for multi-file upload functionality.
This script tests the updated upload endpoints with various scenarios.
"""

import os
import tempfile
import requests
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

def test_single_file_upload():
    """Test single file upload endpoint."""
    print("\n=== Testing Single File Upload ===")
    
    # Create test files
    test_files = []
    
    # Valid TXT file
    txt_content = "This is a test document.\nIt contains multiple lines.\nFor testing purposes."
    txt_file = create_test_file(txt_content, ".txt")
    test_files.append(txt_file)
    
    try:
        with open(txt_file.name, 'rb') as f:
            file_content = f.read()
        
        files = {'file': (os.path.basename(txt_file.name), file_content, 'text/plain')}
        response = requests.post(SINGLE_UPLOAD_ENDPOINT, files=files)
        
        print(f"Single file upload response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['message']}")
            print(f"Total files: {result['total_files']}")
            print(f"Successful: {result['successful_uploads']}")
            print(f"Failed: {result['failed_uploads']}")
            for file_result in result['results']:
                print(f"  - {file_result['filename']}: {file_result['status']}")
                if file_result['status'] == 'success':
                    print(f"    Chunks: {file_result['chunk_count']}")
                    print(f"    Document ID: {file_result['document_id']}")
        else:
            print(f"Error: {response.text}")
    
    finally:
        cleanup_test_files(test_files)

def test_multi_file_upload():
    """Test multi-file upload endpoint."""
    print("\n=== Testing Multi-File Upload ===")
    
    # Create test files
    test_files = []
    
    # Valid files
    txt_content = "This is a test text document.\nIt contains multiple lines.\nFor testing purposes."
    txt_file = create_test_file(txt_content, ".txt")
    test_files.append(txt_file)
    
    txt_content2 = "This is another test document.\nWith different content.\nFor batch testing."
    txt_file2 = create_test_file(txt_content2, ".txt")
    test_files.append(txt_file2)
    
    try:
        files = []
        for file in test_files:
            with open(file.name, 'rb') as f:
                file_content = f.read()
                files.append(('files', (os.path.basename(file.name), file_content, 'text/plain')))
        
        response = requests.post(UPLOAD_ENDPOINT, files=files)
        
        print(f"Multi-file upload response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['message']}")
            print(f"Total files: {result['total_files']}")
            print(f"Successful: {result['successful_uploads']}")
            print(f"Failed: {result['failed_uploads']}")
            for file_result in result['results']:
                print(f"  - {file_result['filename']}: {file_result['status']}")
                if file_result['status'] == 'success':
                    print(f"    Chunks: {file_result['chunk_count']}")
                    print(f"    Document ID: {file_result['document_id']}")
                else:
                    print(f"    Error: {file_result['error_message']}")
        else:
            print(f"Error: {response.text}")
    
    finally:
        cleanup_test_files(test_files)

def test_mixed_valid_invalid_files():
    """Test upload with mix of valid and invalid files."""
    print("\n=== Testing Mixed Valid/Invalid Files ===")
    
    # Create test files
    test_files = []
    
    # Valid TXT file
    txt_content = "This is a valid test document."
    txt_file = create_test_file(txt_content, ".txt")
    test_files.append(txt_file)
    
    # Invalid file (too large)
    large_content = "x" * (11 * 1024 * 1024)  # 11MB
    large_file = create_test_file(large_content, ".txt")
    test_files.append(large_file)
    
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
        
        print(f"Mixed files upload response: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result['message']}")
            print(f"Total files: {result['total_files']}")
            print(f"Successful: {result['successful_uploads']}")
            print(f"Failed: {result['failed_uploads']}")
            for file_result in result['results']:
                print(f"  - {file_result['filename']}: {file_result['status']}")
                if file_result['status'] == 'success':
                    print(f"    Chunks: {file_result['chunk_count']}")
                    print(f"    Document ID: {file_result['document_id']}")
                else:
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
    if response.status_code == 400:
        print("Correctly rejected empty upload")
        print(f"Error: {response.json()['detail']}")
    else:
        print(f"Unexpected response: {response.text}")

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

def main():
    """Run all tests."""
    print("🧪 ClariFlow Multi-File Upload Test Suite")
    print("=" * 50)
    
    # Check server health first
    if not test_server_health():
        print("\nPlease start the server first:")
        print("cd backend")
        print("python main.py")
        return
    
    # Run tests
    test_single_file_upload()
    test_multi_file_upload()
    test_mixed_valid_invalid_files()
    test_empty_upload()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")

if __name__ == "__main__":
    main() 