# ClariFlow Lead Management & CRM Sync System

## Overview

Phase 7 of ClariFlow implements a comprehensive Lead Management system with CRM synchronization capabilities. This system allows you to manage leads, set reminders, and sync data with external CRM platforms like Notion and Airtable.

## Features

### 🎯 Lead Management
- **CRUD Operations**: Create, read, update, and delete leads
- **Lead Status Tracking**: Track leads through different stages (new, contacted, follow-up, converted)
- **Search & Filtering**: Search leads by name, email, phone, source, or notes
- **Pagination**: Efficient pagination for large lead lists
- **Validation**: Email and phone number validation

### 🔔 Reminder System
- **Set Reminders**: Schedule follow-up reminders for leads
- **Upcoming Reminders**: View leads with upcoming reminders
- **Automated Scheduler**: Background scheduler checks for reminders every 15 minutes
- **Logging**: Detailed logging of reminder notifications

### 🔁 CRM Integration
- **Notion Integration**: Sync leads to Notion databases
- **Airtable Integration**: Sync leads to Airtable bases
- **Background Sync**: Asynchronous sync operations
- **Batch Processing**: Efficient batch operations for large datasets
- **Error Handling**: Comprehensive error handling and reporting

## API Endpoints

### Lead Management

#### Create Lead
```http
POST /api/leads
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+1234567890",
  "source": "website",
  "status": "new",
  "notes": "Interested in our services"
}
```

#### Get All Leads
```http
GET /api/leads?skip=0&limit=100&status=new&search=john
```

#### Get Single Lead
```http
GET /api/leads/{lead_id}
```

#### Update Lead
```http
PUT /api/leads/{lead_id}
Content-Type: application/json

{
  "status": "contacted",
  "notes": "Called on 2024-01-15, interested in demo"
}
```

#### Delete Lead
```http
DELETE /api/leads/{lead_id}
```

### Reminder Management

#### Set Reminder
```http
POST /api/leads/{lead_id}/reminder
Content-Type: application/json

{
  "reminder_time": "2024-01-20T10:00:00Z"
}
```

#### Get Upcoming Reminders
```http
GET /api/leads/reminders/upcoming?hours_ahead=24
```

### CRM Integration

#### Sync to CRM
```http
POST /api/crm/sync
Content-Type: application/json

{
  "crm_type": "notion",
  "sync_all": true
}
```

Or sync specific leads:
```http
POST /api/crm/sync
Content-Type: application/json

{
  "crm_type": "airtable",
  "sync_all": false,
  "lead_ids": ["lead-id-1", "lead-id-2"]
}
```

#### Get CRM Status
```http
GET /api/crm/status
```

#### Get Scheduler Status
```http
GET /api/scheduler/status
```

## Data Models

### Lead Model
```python
class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=True)
    source = Column(String, nullable=True)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    reminder_time = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

### Lead Status Enum
```python
class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    FOLLOW_UP = "follow-up"
    CONVERTED = "converted"
```

## Configuration

### Environment Variables

Add these to your `.env` file for CRM integration:

```env
# Notion Integration
NOTION_API_KEY=your_notion_api_key
NOTION_DATABASE_ID=your_notion_database_id

# Airtable Integration
AIRTABLE_API_KEY=your_airtable_api_key
AIRTABLE_BASE_ID=your_airtable_base_id
AIRTABLE_TABLE_NAME=Leads
```

### CRM Setup

#### Notion Setup
1. Create a new integration in Notion
2. Get your API key from the integration settings
3. Share your database with the integration
4. Copy the database ID from the URL
5. Set the environment variables

#### Airtable Setup
1. Get your API key from Airtable account settings
2. Get your base ID from the Airtable URL
3. Create a table named "Leads" (or set AIRTABLE_TABLE_NAME)
4. Set the environment variables

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`

3. Run the application:
```bash
python main.py
```

## Usage Examples

### Python Client Example
```python
import httpx
import asyncio

async def create_lead():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/leads",
            json={
                "name": "Jane Smith",
                "email": "jane@example.com",
                "phone": "+1987654321",
                "source": "referral",
                "status": "new",
                "notes": "Referred by John Doe"
            }
        )
        return response.json()

async def sync_to_notion():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/crm/sync",
            json={
                "crm_type": "notion",
                "sync_all": True
            }
        )
        return response.json()

# Run examples
asyncio.run(create_lead())
asyncio.run(sync_to_notion())
```

### cURL Examples

Create a lead:
```bash
curl -X POST "http://localhost:8000/api/leads" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "source": "website",
    "status": "new"
  }'
```

Get all leads:
```bash
curl "http://localhost:8000/api/leads?limit=10"
```

Set a reminder:
```bash
curl -X POST "http://localhost:8000/api/leads/{lead_id}/reminder" \
  -H "Content-Type: application/json" \
  -d '{
    "reminder_time": "2024-01-20T10:00:00Z"
  }'
```

Sync to Notion:
```bash
curl -X POST "http://localhost:8000/api/crm/sync" \
  -H "Content-Type: application/json" \
  -d '{
    "crm_type": "notion",
    "sync_all": true
  }'
```

## Architecture

### Components

1. **Models** (`app/models/lead.py`): Data models and validation schemas
2. **Service** (`app/services/lead_service.py`): Business logic and CRM integration
3. **API** (`app/api/leads.py`): REST API endpoints
4. **Scheduler** (`app/services/reminder_scheduler.py`): Background reminder processing

### Database Schema

The system creates a `leads` table with the following structure:
- `id`: Unique identifier (UUID)
- `name`: Lead's full name
- `email`: Email address (unique, validated)
- `phone`: Phone number (optional, validated)
- `source`: Lead source (e.g., website, referral)
- `status`: Current status (enum)
- `reminder_time`: Scheduled reminder time
- `notes`: Additional notes
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Background Processing

- **Reminder Scheduler**: Runs every 15 minutes to check for upcoming reminders
- **CRM Sync**: Uses FastAPI BackgroundTasks for asynchronous sync operations
- **Error Handling**: Comprehensive error logging and reporting

## Error Handling

The system includes robust error handling:

- **Validation Errors**: Email and phone validation
- **Duplicate Emails**: Prevents duplicate email addresses
- **CRM API Errors**: Handles API failures gracefully
- **Database Errors**: Transaction rollback on errors
- **Logging**: Detailed error logging for debugging

## Monitoring

### Logs
The system logs all operations:
- Lead creation, updates, and deletions
- Reminder scheduling and notifications
- CRM sync operations and results
- Error conditions and debugging information

### Status Endpoints
- `/api/crm/status`: Check CRM configuration
- `/api/scheduler/status`: Check reminder scheduler status

## Future Enhancements

1. **Email Notifications**: Send email reminders for follow-ups
2. **Dashboard Integration**: Real-time dashboard for lead management
3. **Advanced Analytics**: Lead conversion tracking and reporting
4. **Additional CRM Support**: HubSpot, Salesforce integration
5. **Webhook Support**: Real-time CRM updates
6. **Bulk Operations**: Import/export lead data
7. **Custom Fields**: Configurable lead fields
8. **Lead Scoring**: Automated lead scoring system

## Troubleshooting

### Common Issues

1. **CRM Sync Fails**
   - Check API keys and configuration
   - Verify database/table IDs
   - Check network connectivity

2. **Reminders Not Working**
   - Verify scheduler is running
   - Check timezone settings
   - Review scheduler logs

3. **Validation Errors**
   - Ensure email format is valid
   - Check phone number format
   - Verify required fields are provided

### Debug Mode

Enable debug logging by setting:
```env
LOG_LEVEL=DEBUG
```

## Security Considerations

1. **API Keys**: Store CRM API keys securely in environment variables
2. **Input Validation**: All inputs are validated and sanitized
3. **Database Security**: Use parameterized queries to prevent SQL injection
4. **Rate Limiting**: Consider implementing rate limiting for production
5. **CORS**: Configure CORS properly for production environments

## Performance

- **Pagination**: Efficient pagination for large datasets
- **Indexing**: Database indexes on frequently queried fields
- **Background Processing**: Non-blocking CRM sync operations
- **Caching**: Consider implementing caching for frequently accessed data

## Testing

The system includes comprehensive error handling and validation. For production deployment, consider adding:

1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test API endpoints
3. **CRM Integration Tests**: Test sync functionality
4. **Load Testing**: Test performance under load

## Support

For issues and questions:
1. Check the logs for error details
2. Verify configuration settings
3. Test with the provided examples
4. Review the API documentation at `/docs` 