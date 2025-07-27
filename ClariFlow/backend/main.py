from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, chat, health, search, upload, leads, insights, tasks, composition, crm, agents, workflow, models
from app.core.database import engine, Base
from app.core.config import settings
from app.utils.logger import setup_logger
from app.services.reminder_scheduler import reminder_scheduler

# Create database tables
Base.metadata.create_all(bind=engine)

# Setup logger
logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ClariFlow API",
    description="AI-powered document chat and search API with Lead Management, Business Insights, Task Management, Email/Proposal Composition & CRM Sync",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(leads.router, prefix="/api", tags=["leads"])

# Phase 8 - New Business Insights & Automation Features
app.include_router(insights.router, prefix="/api", tags=["insights"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(composition.router, prefix="/api", tags=["composition"])
app.include_router(crm.router, prefix="/api", tags=["crm"])
app.include_router(agents.router, prefix="/api", tags=["agents"])
app.include_router(workflow.router, prefix="/api", tags=["workflows"])
app.include_router(models.router, prefix="/api", tags=["models"])

@app.on_event("startup")
async def startup_event():
    logger.info("ClariFlow API starting up...")
    logger.info("Database tables created successfully")
    
    # Initialize agents
    try:
        from app.api.agents import initialize_agents
        await initialize_agents()
        logger.info("Agents initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize agents: {str(e)}")
    
    # Start the reminder scheduler
    reminder_scheduler.start()
    logger.info("Reminder scheduler started")
    
    logger.info("Phase 8 Features Loaded:")
    logger.info("- Business Insights & Data Analysis")
    logger.info("- Task Extraction & Management")
    logger.info("- Email & Proposal Composition")
    logger.info("- CRM Sync & Webhook Support")
    logger.info("- Workflow Automation & Audit Logging")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ClariFlow API shutting down...")
    
    # Stop the reminder scheduler
    reminder_scheduler.stop()
    logger.info("Reminder scheduler stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 