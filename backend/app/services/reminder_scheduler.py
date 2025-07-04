from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from ..services.lead_service import LeadService
from ..core.database import SessionLocal
from ..utils.logger import setup_logger

logger = setup_logger(__name__)

class ReminderScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.lead_service = LeadService()
        self.is_running = False
    
    def start(self):
        """Start the reminder scheduler."""
        if not self.is_running:
            # Check for reminders every 15 minutes
            self.scheduler.add_job(
                self.check_reminders,
                IntervalTrigger(minutes=15),
                id='check_reminders',
                name='Check for upcoming lead reminders'
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("Reminder scheduler started")
    
    def stop(self):
        """Stop the reminder scheduler."""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Reminder scheduler stopped")
    
    async def check_reminders(self):
        """Check for upcoming reminders and log them."""
        try:
            # Get database session
            db = SessionLocal()
            try:
                # Get reminders for the next 24 hours
                upcoming_reminders = self.lead_service.get_upcoming_reminders(db, hours_ahead=24)
                
                if upcoming_reminders:
                    logger.info(f"Found {len(upcoming_reminders)} upcoming reminders:")
                    
                    for lead in upcoming_reminders:
                        time_until_reminder = lead.reminder_time - datetime.utcnow()
                        hours_until = time_until_reminder.total_seconds() / 3600
                        
                        if hours_until <= 1:
                            # Reminder is due within the next hour
                            logger.warning(
                                f"URGENT REMINDER: Follow up with {lead.name} ({lead.email}) "
                                f"in {hours_until:.1f} hours. Status: {lead.status.value}"
                            )
                        elif hours_until <= 4:
                            # Reminder is due within the next 4 hours
                            logger.info(
                                f"REMINDER: Follow up with {lead.name} ({lead.email}) "
                                f"in {hours_until:.1f} hours. Status: {lead.status.value}"
                            )
                        else:
                            # Reminder is due later
                            logger.info(
                                f"UPCOMING: Follow up with {lead.name} ({lead.email}) "
                                f"in {hours_until:.1f} hours. Status: {lead.status.value}"
                            )
                        
                        # Log additional details if available
                        if lead.notes:
                            logger.info(f"  Notes: {lead.notes[:100]}{'...' if len(lead.notes) > 100 else ''}")
                        if lead.phone:
                            logger.info(f"  Phone: {lead.phone}")
                        if lead.source:
                            logger.info(f"  Source: {lead.source}")
                else:
                    logger.debug("No upcoming reminders found")
                    
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error checking reminders: {str(e)}")
    
    def get_scheduler_status(self) -> dict:
        """Get the current status of the scheduler."""
        return {
            "is_running": self.is_running,
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()
            ]
        }

# Global scheduler instance
reminder_scheduler = ReminderScheduler() 