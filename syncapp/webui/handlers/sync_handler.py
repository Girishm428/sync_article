from datetime import datetime
import syncapp.config.database as db
from syncapp.backend.sync_runnerv2 import run_sync_async
from syncapp.loggers.log_cli import setup_logger
from nicegui import ui

logger = setup_logger(__name__)

def create_sync_handler(article, refresh_callback, sync_button):
    """
    Creates a sync handler for an article.
    
    Args:
        article (dict): The article data
        refresh_callback (callable): Function to refresh the UI after sync
        sync_button (ui.button): The sync button reference to update its state
    """
    async def handle_sync():
        # Visually disable button and show spinner
        sync_button.props('loading=true')
        
        # Update status in DB and refresh UI to show "Syncing"
        conn = db.get_db_connection()
        conn.execute("UPDATE articles SET status = 'Syncing' WHERE id = ?", (article['id'],))
        conn.commit()
        conn.close()
        refresh_callback()
        logger.info("Syncing article...")
        
        # Run the actual sync
        success, message = await run_sync_async(
            article_id=article['article_id'],
            source_url=article['source_url'],
            title=article['title']
        )
        ui.notify(message, type='positive' if success else 'negative')
        
        # Update DB with final status
        conn = db.get_db_connection()
        new_status = 'Success' if success else 'Failed'
        last_synced_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn.execute("UPDATE articles SET status = ?, last_synced = ? WHERE id = ?", 
                     (new_status, last_synced_time, article['id']))
        conn.commit()
        conn.close()
        
        # Reset button state and refresh the grid
        sync_button.props('loading=false')
        refresh_callback()
    
    return handle_sync

def create_bulk_sync_handler(selected_articles, refresh_callback):
    """
    Creates a bulk sync handler for multiple articles.
    
    Args:
        selected_articles (set): Set of selected article IDs
        refresh_callback (callable): Function to refresh the UI after sync
    """
    async def handle_bulk_sync():
        if not selected_articles:
            ui.notify('Please select at least one article to sync', type='warning')
            return

        # Create a sync button for visual feedback
        sync_button = ui.button(icon='sync').props('loading=true flat round color=primary')
        
        try:
            # Update status to Syncing for selected articles
            conn = db.get_db_connection()
            conn.execute("UPDATE articles SET status = 'Syncing' WHERE id IN ({})".format(
                ','.join('?' * len(selected_articles))
            ), list(selected_articles))
            conn.commit()
            conn.close()
            
            refresh_callback()
            logger.info(f"Syncing {len(selected_articles)} articles...")

            # Sync each article
            for article_id in selected_articles:
                article = db.get_db_connection().execute(
                    'SELECT * FROM articles WHERE id = ?', (article_id,)
                ).fetchone()
                
                if article:
                    success, message = await run_sync_async(
                        article_id=article['article_id'],
                        source_url=article['source_url'],
                        title=article['title']
                    )
                    ui.notify(message, type='positive' if success else 'negative')
                    
                    # Update status
                    conn = db.get_db_connection()
                    new_status = 'Success' if success else 'Failed'
                    last_synced_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    conn.execute(
                        "UPDATE articles SET status = ?, last_synced = ? WHERE id = ?",
                        (new_status, last_synced_time, article_id)
                    )
                    conn.commit()
                    conn.close()

            ui.notify(f'Successfully synced {len(selected_articles)} articles', type='positive')
        except Exception as e:
            ui.notify(f'Error during bulk sync: {str(e)}', type='negative')
        finally:
            sync_button.delete()
            refresh_callback()
    
    return handle_bulk_sync


