# ClariFlow OpenRouter Integration

This document describes the implementation of multiple OpenRouter.ai models with dynamic routing for different use cases in ClariFlow.

## 🎯 Overview

ClariFlow now supports multiple AI models via OpenRouter.ai with intelligent routing based on feature type. This allows for:
- **Optimized model selection** for different tasks
- **Automatic fallback** mechanisms
- **Cost-effective** usage of free tier models
- **Scalable** architecture for adding new models

## 🔧 Supported Models

### Free OpenRouter.ai Models
- `deepseek/deepseek-chat-v3-0324` - High-performance chat model
- `deepseek/deepseek-r1-zero` - Efficient reasoning model
- `qwen/qwen3-4b-instruct` - Fast chat and general tasks
- `qwen/qwen3-14b-instruct` - Advanced reasoning and analysis
- `mistralai/mistral-small-3.1-24b-instruct` - Balanced performance model
- `openrouter/cypher-alpha` - Specialized for search and Q&A
- `openrouter/optimus-alpha` - Optimized for task extraction

### Model Assignments by Feature

| Feature | Primary Model | Fallback Model | Use Case |
|---------|---------------|----------------|----------|
| **Chat** | `qwen3-4b-instruct` | `deepseek-chat-v3-0324` | Conversational interactions |
| **Search/Q&A** | `qwen3-14b-instruct` | `cypher-alpha` | Document search and questions |
| **Summarization** | `mistral-24b-instruct` | `deepseek-r1-zero` | Content summarization |
| **Insights** | `mistral-24b-instruct` | `deepseek-r1-zero` | Data analysis and insights |
| **Composition** | `deepseek-chat-v3-0324` | `mistral-24b-instruct` | Email/proposal writing |
| **Task Extraction** | `optimus-alpha` | `qwen3-4b-instruct` | Task parsing and extraction |

## 🚀 Setup Instructions

### 1. Environment Configuration

Update your `.env` file with OpenRouter configuration:

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your-openrouter-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
AI_DEFAULT_MODEL=deepseek/deepseek-chat-v3-0324

# Existing OpenAI (fallback)
OPENAI_API_KEY=your-openai-key-here
```

### 2. Get OpenRouter API Key

1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up for a free account
3. Navigate to your API keys section
4. Copy your API key
5. Add it to your `.env` file

### 3. Test the Integration

Run the test script to verify everything is working:

```bash
cd backend
python test_openrouter_integration.py
```

## 🏗️ Architecture

### Core Components

#### 1. Model Router (`app/utils/model_router.py`)
- **Dynamic model selection** based on feature type
- **Automatic fallback** to alternative models
- **Configuration management** for model assignments
- **Error handling** and retry logic

#### 2. AI Client (`app/services/ai_client.py`)
- **Unified interface** for both OpenRouter and OpenAI
- **Feature-specific methods** for different use cases
- **Service status monitoring**
- **Automatic fallback** between services

#### 3. API Endpoints (`app/api/models.py`)
- `GET /api/models/` - Get all model information
- `GET /api/models/status` - Check service status
- `GET /api/models/features` - Get feature configurations

### Service Integration

All existing AI-powered services now use the new routing system:

- **Chat Service** (`app/services/chat_service.py`)
- **Composition Service** (`app/services/composition_service.py`)
- **Insights Service** (`app/services/insight_service.py`)
- **Search Service** (enhanced with AI responses)

## 📊 API Usage

### Get Model Information

```bash
curl http://localhost:8000/api/models/
```

Response:
```json
{
  "models": {
    "supported_models": ["deepseek/deepseek-chat-v3-0324", ...],
    "feature_configurations": [
      {
        "feature_type": "chat",
        "primary_model": "qwen/qwen3-4b-instruct",
        "fallback_model": "deepseek/deepseek-chat-v3-0324",
        "description": "Optimized for conversational interactions"
      }
    ],
    "api_base_url": "https://openrouter.ai/api/v1",
    "api_configured": true
  },
  "service_status": {
    "openrouter_configured": true,
    "openai_configured": true,
    "default_service": "openrouter",
    "supported_features": ["chat", "search", "summarization", ...]
  }
}
```

### Check Service Status

```bash
curl http://localhost:8000/api/models/status
```

### Get Feature Configurations

```bash
curl http://localhost:8000/api/models/features
```

## 🔄 Fallback Mechanism

The system implements a robust fallback strategy:

1. **Primary Model** - Selected based on feature type
2. **Fallback Model** - Alternative model for the same feature
3. **OpenAI Fallback** - If OpenRouter fails, fall back to OpenAI
4. **Error Handling** - Graceful degradation with informative messages

### Fallback Flow

```
Feature Request → Primary Model → Success ✅
                ↓ (if fails)
                Fallback Model → Success ✅
                ↓ (if fails)
                OpenAI GPT-4 → Success ✅
                ↓ (if fails)
                Error Response ❌
```

## 🎛️ Configuration Options

### Model Assignments

You can modify model assignments in `app/utils/model_router.py`:

```python
self.model_configs = {
    FeatureType.CHAT: {
        "primary": "qwen/qwen3-4b-instruct",
        "fallback": "deepseek/deepseek-chat-v3-0324",
        "description": "Optimized for conversational interactions"
    },
    # Add more configurations...
}
```

### API Parameters

Customize API calls in `app/services/ai_client.py`:

```python
# Example: Customize temperature and max_tokens
response = await ai_client.chat_response(
    query="Hello",
    max_tokens=1000,
    temperature=0.7
)
```

## 📈 Monitoring and Logging

### Logging

All model selections and API calls are logged:

```python
logger.info(f"Selected model '{model}' for feature '{feature_type.value}'")
logger.info(f"Using OpenRouter for {feature_type.value}")
logger.info(f"Falling back to OpenAI")
```

### Performance Monitoring

Track model performance with response metadata:

```json
{
  "content": "AI response...",
  "model_used": "qwen/qwen3-4b-instruct",
  "feature_type": "chat",
  "tokens_used": 150,
  "success": true
}
```

## 🧪 Testing

### Run Integration Tests

```bash
# Test without API keys
python test_openrouter_integration.py

# Test with actual API calls (requires API keys)
python -m pytest tests/test_openrouter.py
```

### Manual Testing

1. **Start the server**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Test chat endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "Hello, how are you?"}'
   ```

3. **Test composition endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/compose/email \
     -H "Content-Type: application/json" \
     -d '{"subject": "Test", "context": "Test email"}'
   ```

## 🔧 Troubleshooting

### Common Issues

1. **API Key Not Configured**
   ```
   Error: OPENROUTER_API_KEY not configured
   Solution: Add your OpenRouter API key to .env file
   ```

2. **Model Not Available**
   ```
   Error: Model not available on OpenRouter
   Solution: Check model availability or use fallback
   ```

3. **Rate Limiting**
   ```
   Error: Rate limit exceeded
   Solution: Implement rate limiting or use different models
   ```

### Debug Mode

Enable debug logging in `.env`:

```bash
LOG_LEVEL=DEBUG
```

### Service Status Check

```bash
curl http://localhost:8000/api/models/status
```

## 🚀 Deployment

### Production Considerations

1. **API Key Security**
   - Use environment variables
   - Rotate keys regularly
   - Monitor usage

2. **Rate Limiting**
   - Implement request throttling
   - Monitor API usage
   - Set up alerts

3. **Error Handling**
   - Graceful degradation
   - User-friendly error messages
   - Fallback mechanisms

4. **Monitoring**
   - Track model performance
   - Monitor costs
   - Log usage patterns

## 📚 Additional Resources

- [OpenRouter.ai Documentation](https://openrouter.ai/docs)
- [Model Performance Comparison](https://openrouter.ai/models)
- [API Reference](https://openrouter.ai/docs/api)
- [Cost Calculator](https://openrouter.ai/pricing)

## 🤝 Contributing

To add new models or modify configurations:

1. Update `model_configs` in `app/utils/model_router.py`
2. Test with `test_openrouter_integration.py`
3. Update documentation
4. Submit pull request

## 📄 License

This integration is part of ClariFlow and follows the same license terms. 