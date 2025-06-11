import syncapp.config.database as db
from datetime import datetime
from nicegui import ui
from syncapp.webui.pages.header import header
from syncapp.loggers.log_cli import setup_logger
from syncapp.webui.handlers.sync_handler import create_sync_handler
from syncapp.webui.handlers.edit_handler import create_edit_handler
from syncapp.webui.handlers.delete_handler import create_delete_handler
from syncapp.backend.sync_runnerv2 import run_sync_async

logger = setup_logger(__name__)

# -----------------
# Page 2: List Articles
# -----------------
@ui.page('/list')
def list_page():
    header()

    ui.label('Articles Pending Sync').classes('text-h5 w-full text-center my-4')

    # Store selected article IDs
    selected_articles = set()

    def handle_select_all(checked):
        if checked:
            # Get all article IDs
            articles = db.get_db_connection().execute('SELECT id FROM articles').fetchall()
            selected_articles.update(article['id'] for article in articles)
        else:
            selected_articles.clear()
        article_grid.refresh()

    def handle_article_select(article_id, checked):
        if checked:
            selected_articles.add(article_id)
        else:
            selected_articles.discard(article_id)

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
            
            article_grid.refresh()
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
            article_grid.refresh()

    def handle_bulk_delete():
        if not selected_articles:
            ui.notify('Please select at least one article to delete', type='warning')
            return

        dialog = ui.dialog()
        with dialog, ui.card().classes('w-full max-w-lg'):
            ui.label('Delete Articles').classes('text-h5 q-mb-md')
            ui.label(f'Are you sure you want to delete {len(selected_articles)} articles?').classes('q-mb-md')
            
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Delete', on_click=lambda: delete_selected_articles(dialog)).props('flat color=negative')
        dialog.open()

    def delete_selected_articles(dialog):
        try:
            conn = db.get_db_connection()
            conn.execute("DELETE FROM articles WHERE id IN ({})".format(
                ','.join('?' * len(selected_articles))
            ), list(selected_articles))
            conn.commit()
            conn.close()
            
            ui.notify(f'Successfully deleted {len(selected_articles)} articles', type='positive')
            dialog.close()
            selected_articles.clear()
            article_grid.refresh()
        except Exception as e:
            ui.notify(f'Error deleting articles: {str(e)}', type='negative')

    # Bulk action buttons
    with ui.row().classes('w-full max-w-7xl mx-auto mb-4 justify-end gap-2'):
        ui.button('Sync Selected', icon='sync', on_click=handle_bulk_sync).props('flat color=primary')
        ui.button('Delete Selected', icon='delete', on_click=handle_bulk_delete).props('flat color=negative')

    # A container that we can refresh
    @ui.refreshable
    def article_grid():
        articles = db.get_db_connection().execute('SELECT * FROM articles ORDER BY id DESC').fetchall()
        
        if not articles:
            with ui.card().classes('w-full max-w-3xl mx-auto'):
                ui.label('No articles have been added yet.').classes('text-center')
            return

        with ui.grid(columns=7).classes('w-full max-w-7xl mx-auto gap-4 items-center'):
            # Grid Headers
            ui.checkbox('', on_change=handle_select_all).classes('justify-self-center')
            ui.label('Title').classes('font-bold col-span-1')
            ui.label('Source URL').classes('font-bold col-span-1')
            ui.label('Zendesk ID').classes('font-bold')
            ui.label('Status').classes('font-bold')
            ui.label('Last Synced').classes('font-bold')
            ui.label('Action').classes('font-bold')

            # Grid Rows
            for article in articles:
                ui.checkbox('', value=article['id'] in selected_articles, 
                          on_change=lambda e, id=article['id']: handle_article_select(id, e.value)).classes('justify-self-center')
                ui.label(article['title']).classes('col-span-1 truncate')
                with ui.link(target=article['source_url']).classes('col-span-1'):
                    ui.label(article['source_url'][:30] + '...').classes('text-blue-500 cursor-pointer truncate')
                ui.label(article['article_id']).classes('truncate')
                ui.label(article['status']).classes(f"p-1 rounded text-white {'bg-green-500' if article['status'] == 'Success' else 'bg-red-500' if article['status'] == 'Failed' else 'bg-yellow-500' if article['status'] == 'Syncing' else 'bg-gray-400'}")
                ui.label(article['last_synced'] or 'Never').classes('truncate')
                with ui.row().classes('gap-2'):
                    sync_button = ui.button(icon='sync').props('flat round color=primary')
                    sync_button.on_click(create_sync_handler(article, article_grid.refresh, sync_button))
                    ui.button(icon='edit', on_click=create_edit_handler(article, article_grid.refresh)).props('flat round color=secondary')
                    ui.button(icon='delete', on_click=create_delete_handler(article, article_grid.refresh)).props('flat round color=negative')
    
    # Initial drawing of the grid
    article_grid()

