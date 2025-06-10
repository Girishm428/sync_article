import syncapp.config.database as db
from syncapp.backend.sync_runnerv2 import run_sync_async
from datetime import datetime
from nicegui import ui
from syncapp.webui.pages.header import header
from syncapp.loggers.log_cli import setup_logger

logger = setup_logger(__name__)

# -----------------
# Page 2: List Articles
# -----------------
@ui.page('/list')
def list_page():
    header()

    ui.label('Articles Pending Sync').classes('text-h5 w-full text-center my-4')

    # A container that we can refresh
    @ui.refreshable
    def article_grid():
        articles = db.get_db_connection().execute('SELECT * FROM articles ORDER BY id DESC').fetchall()
        
        if not articles:
            with ui.card().classes('w-full max-w-3xl mx-auto'):
                ui.label('No articles have been added yet.').classes('text-center')
            return

        with ui.grid(columns=6).classes('w-full max-w-5xl mx-auto gap-4 items-center'):
            # Grid Headers
            ui.label('Title').classes('font-bold')
            ui.label('Source URL').classes('font-bold')
            ui.label('Zendesk ID').classes('font-bold')
            ui.label('Status').classes('font-bold')
            ui.label('Last Synced').classes('font-bold')
            ui.label('Action').classes('font-bold')

            # Grid Rows
            for article in articles:
                # Use a closure to capture the article for the handler
                def create_sync_handler(art):
                    async def handle_sync():
                        # Visually disable button and show spinner
                        sync_button.props('loading=true')
                        
                        # Update status in DB and refresh UI to show "Syncing"
                        conn = db.get_db_connection()
                        conn.execute("UPDATE articles SET status = 'Syncing' WHERE id = ?", (art['id'],))
                        conn.commit()
                        conn.close()
                        article_grid.refresh()
                        logger.info("Syncing article...")
                        # Run the actual sync
                        success, message = await run_sync_async(
                            article_id=art['article_id'],
                            source_url=art['source_url'],
                            title=art['title']
                        )
                        ui.notify(message, type='positive' if success else 'negative')
                        
                        # Update DB with final status
                        conn = db.get_db_connection()
                        new_status = 'Success' if success else 'Failed'
                        last_synced_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        conn.execute("UPDATE articles SET status = ?, last_synced = ? WHERE id = ?", 
                                     (new_status, last_synced_time, art['id']))
                        conn.commit()
                        conn.close()
                        
                        # Refresh the grid again to show the final status
                        article_grid.refresh()
                    return handle_sync

                ui.label(article['title'])
                with ui.link(target=article['source_url']):
                    ui.label(article['source_url'][:30] + '...').classes('text-blue-500 cursor-pointer')
                ui.label(article['article_id'])
                ui.label(article['status']).classes(f"p-1 rounded text-white {'bg-green-500' if article['status'] == 'Success' else 'bg-red-500' if article['status'] == 'Failed' else 'bg-yellow-500' if article['status'] == 'Syncing' else 'bg-gray-400'}")
                ui.label(article['last_synced'] or 'Never')
                sync_button = ui.button(icon='sync', on_click=create_sync_handler(article)).props('flat round color=primary')
    
    # Initial drawing of the grid
    article_grid()

