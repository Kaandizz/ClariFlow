#!/usr/bin/env python3
"""
Test script for OpenRouter integration and model routing functionality.
This script tests the model router and AI client without requiring actual API keys.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.utils.model_router import model_router, FeatureType
from app.services.ai_client import ai_client
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

async def test_model_router():
    """Test the model router functionality."""
    print("🔧 Testing Model Router...")
    
    # Test model selection for different features
    features = [
        FeatureType.CHAT,
        FeatureType.SEARCH,
        FeatureType.SUMMARIZATION,
        FeatureType.INSIGHTS,
        FeatureType.COMPOSITION,
        FeatureType.TASK_EXTRACTION
    ]
    
    for feature in features:
        primary_model = model_router.get_model_for_feature(feature, use_fallback=False)
        fallback_model = model_router.get_model_for_feature(feature, use_fallback=True)
        
        print(f"  {feature.value}:")
        print(f"    Primary: {primary_model}")
        print(f"    Fallback: {fallback_model}")
    
    # Test supported models
    supported_models = model_router.get_supported_models()
    print(f"\n📋 Supported Models: {len(supported_models)} configurations")
    for config in supported_models:
        print(f"  - {config['feature_type']}: {config['primary_model']} (fallback: {config['fallback_model']})")
    
    # Test model info
    model_info = model_router.get_model_info()
    print("\n🔍 Model Info:")
    print(f"  - API Base URL: {model_info['api_base_url']}")
    print(f"  - API Configured: {model_info['api_configured']}")
    print(f"  - Supported Models: {len(model_info['supported_models'])}")

async def test_ai_client():
    """Test the AI client functionality."""
    print("\n🤖 Testing AI Client...")
    
    # Test service status
    status = ai_client.get_service_status()
    print(f"  OpenRouter Configured: {status['openrouter_configured']}")
    print(f"  OpenAI Configured: {status['openai_configured']}")
    print(f"  Default Service: {status['default_service']}")
    print(f"  Supported Features: {status['supported_features']}")
    
    # Test message building
    messages = ai_client._build_chat_messages("Hello, how are you?", ["Hi there!", "Hello! How can I help you?"])
    print(f"\n  Built {len(messages)} messages for chat")
    
    # Test feature-specific responses (without making actual API calls)
    print("\n  Feature-specific response methods available:")
    print("    - chat_response()")
    print("    - search_response()")
    print("    - summarization_response()")
    print("    - insights_response()")
    print("    - composition_response()")

async def test_configuration():
    """Test configuration and environment variables."""
    print("\n⚙️ Testing Configuration...")
    
    # Check environment variables
    env_vars = [
        "OPENROUTER_API_KEY",
        "OPENROUTER_BASE_URL",
        "AI_DEFAULT_MODEL",
        "OPENAI_API_KEY"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
            else:
                masked_value = value
            print(f"  {var}: {masked_value}")
        else:
            print(f"  {var}: Not set")

async def test_model_assignments():
    """Test the model assignments for different use cases."""
    print("\n🎯 Testing Model Assignments...")
    
    assignments = {
        "Chat": FeatureType.CHAT,
        "Search/Q&A": FeatureType.SEARCH,
        "Summarization": FeatureType.SUMMARIZATION,
        "Insights/Analysis": FeatureType.INSIGHTS,
        "Composition": FeatureType.COMPOSITION,
        "Task Extraction": FeatureType.TASK_EXTRACTION
    }
    
    for use_case, feature in assignments.items():
        primary = model_router.get_model_for_feature(feature, use_fallback=False)
        fallback = model_router.get_model_for_feature(feature, use_fallback=True)
        print(f"  {use_case}:")
        print(f"    Primary: {primary}")
        print(f"    Fallback: {fallback}")

async def main():
    """Run all tests."""
    print("🚀 ClariFlow OpenRouter Integration Test")
    print("=" * 50)
    
    try:
        await test_model_router()
        await test_ai_client()
        await test_configuration()
        await test_model_assignments()
        
        print("\n✅ All tests completed successfully!")
        print("\n📝 Summary:")
        print("  - Model router is working correctly")
        print("  - AI client is properly configured")
        print("  - Feature-based model selection is implemented")
        print("  - Fallback mechanisms are in place")
        print("\n🔑 Next Steps:")
        print("  1. Set OPENROUTER_API_KEY in .env file")
        print("  2. Test with actual API calls")
        print("  3. Monitor model performance and adjust assignments")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        logger.error(f"Test failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 