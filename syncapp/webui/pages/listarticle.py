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

        with ui.grid(columns=6).classes('w-full max-w-7xl mx-auto gap-4 items-center'):
            # Grid Headers
            ui.label('Title').classes('font-bold col-span-1')
            ui.label('Source URL').classes('font-bold col-span-1')
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

                def create_edit_handler(art):
                    def handle_edit():
                        dialog = ui.dialog()
                        with dialog, ui.card().classes('w-full max-w-lg'):
                            ui.label('Edit Article').classes('text-h5 q-mb-md')
                            
                            title_input = ui.input('Title', value=art['title']).classes('w-full')
                            url_input = ui.input('Source URL', value=art['source_url']).classes('w-full')
                            zendesk_id_input = ui.input('Zendesk ID', value=art['article_id']).classes('w-full')
                            
                            with ui.row().classes('w-full justify-end'):
                                ui.button('Cancel', on_click=dialog.close).props('flat')
                                ui.button('Save', on_click=lambda: save_changes(
                                    art['id'],
                                    title_input.value,
                                    url_input.value,
                                    zendesk_id_input.value,
                                    dialog
                                )).props('flat color=primary')
                        dialog.open()
                    
                    def save_changes(article_id, new_title, new_url, new_zendesk_id, dialog):
                        try:
                            # Validate all fields are filled
                            if not new_title.strip():
                                ui.notify('Title cannot be empty', type='negative')
                                return
                            if not new_url.strip():
                                ui.notify('Source URL cannot be empty', type='negative')
                                return
                            if not new_zendesk_id.strip():
                                ui.notify('Zendesk ID cannot be empty', type='negative')
                                return

                            conn = db.get_db_connection()
                            conn.execute("""
                                UPDATE articles 
                                SET title = ?, source_url = ?, article_id = ?, status = 'Pending'
                                WHERE id = ?
                            """, (new_title, new_url, new_zendesk_id, article_id))
                            conn.commit()
                            conn.close()
                            
                            ui.notify('Article updated successfully!', type='positive')
                            dialog.close()
                            article_grid.refresh()
                        except Exception as e:
                            ui.notify(f'Error updating article: {str(e)}', type='negative')
                    
                    return handle_edit

                def create_delete_handler(art):
                    def handle_delete():
                        dialog = ui.dialog()
                        with dialog, ui.card().classes('w-full max-w-lg'):
                            ui.label('Delete Article').classes('text-h5 q-mb-md')
                            ui.label(f'Are you sure you want to delete "{art["title"]}"?').classes('q-mb-md')
                            
                            with ui.row().classes('w-full justify-end'):
                                ui.button('Cancel', on_click=dialog.close).props('flat')
                                ui.button('Delete', on_click=lambda: delete_article(art['id'], dialog)).props('flat color=negative')
                        dialog.open()
                    
                    def delete_article(article_id, dialog):
                        try:
                            conn = db.get_db_connection()
                            conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
                            conn.commit()
                            conn.close()
                            
                            ui.notify('Article deleted successfully!', type='positive')
                            dialog.close()
                            article_grid.refresh()
                        except Exception as e:
                            ui.notify(f'Error deleting article: {str(e)}', type='negative')
                    
                    return handle_delete

                ui.label(article['title']).classes('col-span-1 truncate')
                with ui.link(target=article['source_url']).classes('col-span-1'):
                    ui.label(article['source_url'][:30] + '...').classes('text-blue-500 cursor-pointer truncate')
                ui.label(article['article_id']).classes('truncate')
                ui.label(article['status']).classes(f"p-1 rounded text-white {'bg-green-500' if article['status'] == 'Success' else 'bg-red-500' if article['status'] == 'Failed' else 'bg-yellow-500' if article['status'] == 'Syncing' else 'bg-gray-400'}")
                ui.label(article['last_synced'] or 'Never').classes('truncate')
                with ui.row().classes('gap-2'):
                    sync_button = ui.button(icon='sync', on_click=create_sync_handler(article)).props('flat round color=primary')
                    ui.button(icon='edit', on_click=create_edit_handler(article)).props('flat round color=secondary')
                    ui.button(icon='delete', on_click=create_delete_handler(article)).props('flat round color=negative')

    # Initial drawing of the grid
    article_grid()

