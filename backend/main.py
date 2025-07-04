from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import chat, health, search, upload, leads, insights, tasks, composition, crm
from app.core.database import engine, Base
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
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(leads.router, prefix="/api", tags=["leads"])

# Phase 8 - New Business Insights & Automation Features
app.include_router(insights.router, prefix="/api", tags=["insights"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])
app.include_router(composition.router, prefix="/api", tags=["composition"])
app.include_router(crm.router, prefix="/api", tags=["crm"])

@app.on_event("startup")
async def startup_event():
    logger.info("ClariFlow API starting up...")
    logger.info("Database tables created successfully")
    
    # Start the reminder scheduler
    reminder_scheduler.start()
    logger.info("Reminder scheduler started")
    
    logger.info("Phase 8 Features Loaded:")
    logger.info("- Business Insights & Data Analysis")
    logger.info("- Task Extraction & Management")
    logger.info("- Email & Proposal Composition")
    logger.info("- CRM Sync & Webhook Support")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("ClariFlow API shutting down...")
    
    # Stop the reminder scheduler
    reminder_scheduler.stop()
    logger.info("Reminder scheduler stopped")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 