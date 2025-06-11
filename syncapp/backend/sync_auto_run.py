import asyncio
import schedule
import time
from datetime import datetime
import syncapp.config.database as db
from syncapp.backend.sync_runnerv2 import run_sync_async
from syncapp.loggers.log_cli import setup_logger

logger = setup_logger(__name__)

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
            
            # Check if current time matches the schedule
            if now.hour != hour or now.minute != minute:
                return False
                
            # Check day of month
            if day != '*' and int(day) != now.day:
                return False
                
            # Check month
            if month != '*' and int(month) != now.month:
                return False
                
            # Check weekday (0 = Sunday)
            if weekday != '*' and int(weekday) != now.weekday():
                return False
                
            return True
    except Exception as e:
        logger.error(f"Error parsing cron schedule {cron_schedule}: {str(e)}")
        return False
    return False

async def run_scheduled_sync(article):
    """Run sync for a single article."""
    try:
        # Check if it's time to run this article's schedule
        if not should_run_now(article['cron_schedule']):
            return
            
        logger.info(f"Running scheduled sync for article: {article['title']}")
        success, message = await run_sync_async(
            article_id=article['article_id'],
            source_url=article['source_url'],
            title=article['title']
        )
        
        # Log the result
        logger.info(f"Sync result for {article['title']}: {message}")
        
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
            logger.info(f"Database updated for article: {article['title']}")
        except Exception as db_error:
            logger.error(f"Database update failed for article {article['title']}: {str(db_error)}")
        
        logger.info(f"Scheduled sync completed for article: {article['title']} - Status: {new_status}")
    except Exception as e:
        logger.error(f"Error during scheduled sync for article {article['title']}: {str(e)}")

async def check_scheduled_articles():
    """Check for articles that need to be synced based on their cron schedule."""
    try:
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
        
        # Run sync for each article
        for article in articles:
            await run_scheduled_sync(article)
            
    except Exception as e:
        logger.error(f"Error checking scheduled articles: {str(e)}")

def run_check_scheduled_articles():
    """Run the async check_scheduled_articles function in the event loop."""
    asyncio.run(check_scheduled_articles())

def start_scheduler():
    """Start the scheduler to check for scheduled articles every minute."""
    logger.info("Starting scheduler for cron-based syncs")
    
    # Schedule the check to run every minute
    schedule.every(1).minutes.do(run_check_scheduled_articles)
    
    # Run the scheduler in a loop
    while True:
        schedule.run_pending()
        time.sleep(1)

def run_scheduler():
    """Run the scheduler in a separate thread."""
    import threading
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler thread started") 