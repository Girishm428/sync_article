import asyncio
import schedule
import time
from datetime import datetime
import syncapp.config.database as db
from syncapp.backend.sync_runnerv2 import run_sync_async
from syncapp.loggers.log_cli import setup_logger
import threading
import traceback

logger = setup_logger(__name__)

# Global flag to track scheduler status
scheduler_running = False

def should_run_now(cron_schedule):
    """Check if the cron schedule should run now."""
    try:
        parts = cron_schedule.split()
        if len(parts) >= 6:
            minute = int(parts[1])
            hour = int(parts[2])
            day = parts[3]
            month = parts[4]
            weekday = parts[5]
            
            now = datetime.now()
            logger.info("Checking schedule: %s", cron_schedule)
            logger.info("Current time: %s:%s, Day: %s, Month: %s, Weekday: %s", 
                       now.hour, now.minute, now.day, now.month, now.weekday())
            logger.info("Schedule time: %s:%s, Day: %s, Month: %s, Weekday: %s",
                       hour, minute, day, month, weekday)
            
            # Check if current time matches the schedule
            if now.hour != hour or now.minute != minute:
                logger.info("Time does not match schedule")
                return False
                
            # Check day of month
            if day != '*' and int(day) != now.day:
                logger.info("Day does not match schedule")
                return False
                
            # Check month
            if month != '*' and int(month) != now.month:
                logger.info("Month does not match schedule")
                return False
                
            # Check weekday (0 = Sunday)
            if weekday != '*' and int(weekday) != now.weekday():
                logger.info("Weekday does not match schedule")
                return False
                
            logger.info("Schedule matches current time - will run sync")
            return True
    except Exception as e:
        logger.error("Error parsing cron schedule %s: %s", cron_schedule, str(e))
        return False
    return False

async def run_scheduled_sync(article):
    """Run sync for a single article."""
    try:
        # Check if it's time to run this article's schedule
        if not should_run_now(article['cron_schedule']):
            return
            
        logger.info("Running scheduled sync for article: %s", article['title'])
        success, message = await run_sync_async(
            article_id=article['article_id'],
            source_url=article['source_url'],
            title=article['title']
        )
        
        # Log the result
        logger.info("Sync result for %s: %s", article['title'], message)
        
        # Update sync status in database
        try:
            conn = db.get_db_connection()
            new_status = 'Success' if success else 'Failed'
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # First update the status and last_synced
            conn.execute("""
                UPDATE articles 
                SET status = ?, last_synced = ?
                WHERE id = ?
            """, (new_status, current_time, article['id']))
            
            # Then update last_cron_update
            conn.execute("""
                UPDATE articles 
                SET last_cron_update = ?
                WHERE id = ?
            """, (current_time, article['id']))
            
            conn.commit()
            conn.close()
            logger.info("Database updated for article: %s", article['title'])
        except Exception as db_error:
            logger.error("Database update failed for article %s: %s", 
                        article['title'], str(db_error))
        
        logger.info("Scheduled sync completed for article: %s - Status: %s", 
                   article['title'], new_status)
    except Exception as e:
        logger.error("Error during scheduled sync for article %s: %s", 
                    article['title'], str(e))

async def check_scheduled_articles():
    """Check for articles that need to be synced based on their cron schedule."""
    try:
        logger.info("Checking for scheduled articles...")
        conn = db.get_db_connection()
        cursor = conn.cursor()
        
        # Get all articles with cron schedules
        cursor.execute("""
            SELECT * FROM articles 
            WHERE cron_schedule IS NOT NULL 
            AND cron_schedule != ''
        """)
        
        articles = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        logger.info("Found %d articles with cron schedules", len(articles))
        
        # Run sync for each article
        for article in articles:
            await run_scheduled_sync(article)
            
    except Exception as e:
        logger.error("Error checking scheduled articles: %s", str(e))

def run_check_scheduled_articles():
    """Run the async check_scheduled_articles function in the event loop."""
    logger.info("Starting scheduled check...")
    try:
        asyncio.run(check_scheduled_articles())
        logger.info("Scheduled check completed")
    except Exception as e:
        logger.error("Error in scheduled check: %s", str(e))
        logger.error("Traceback: %s", traceback.format_exc())

def start_scheduler():
    """Start the scheduler to check for scheduled articles every minute."""
    global scheduler_running
    try:
        logger.info("Starting scheduler for cron-based syncs")
        scheduler_running = True
        
        # Schedule the check to run every minute
        schedule.every(1).minutes.do(run_check_scheduled_articles)
        logger.info("Scheduled check configured to run every minute")
        
        # Run the scheduler in a loop
        while scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error("Error in scheduler loop: %s", str(e))
                logger.error("Traceback: %s", traceback.format_exc())
                time.sleep(1)  # Wait a bit before retrying
    except Exception as e:
        logger.error("Fatal error in scheduler: %s", str(e))
        logger.error("Traceback: %s", traceback.format_exc())
        scheduler_running = False

def run_scheduler():
    """Run the scheduler in a separate thread."""
    global scheduler_running
    try:
        logger.info("Initializing scheduler thread...")
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()
        logger.info("Scheduler thread started with ID: %s", scheduler_thread.ident)
        
        # Verify thread is running
        if scheduler_thread.is_alive():
            logger.info("Scheduler thread is running")
        else:
            logger.error("Scheduler thread failed to start")
            
    except Exception as e:
        logger.error("Error starting scheduler thread: %s", str(e))
        logger.error("Traceback: %s", traceback.format_exc())
        scheduler_running = False

def stop_scheduler():
    """Stop the scheduler."""
    global scheduler_running
    logger.info("Stopping scheduler...")
    scheduler_running = False 