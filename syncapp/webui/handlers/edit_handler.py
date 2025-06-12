import syncapp.config.database as db
from nicegui import ui
from syncapp.loggers.log_cli import setup_logger

logger = setup_logger(__name__)

def create_edit_handler(article, refresh_callback):
    """
    Creates an edit handler for an article.
    
    Args:
        article (dict): The article data
        refresh_callback (callable): Function to refresh the UI after edit
    """
    def handle_edit():
        dialog = ui.dialog()
        with dialog, ui.card().classes('w-full max-w-lg'):
            ui.label('Edit Article').classes('text-h5 q-mb-md')
            
            title_input = ui.input('Title', value=article['title']).classes('w-full')
            url_input = ui.input('Source URL', value=article['source_url']).classes('w-full')
            zendesk_id_input = ui.input('Zendesk ID', value=article['article_id']).classes('w-full')
            
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=lambda: save_changes(
                    article['id'],
                    title_input.value,
                    url_input.value,
                    zendesk_id_input.value,
                    dialog
                )).props('flat color=primary')
        dialog.open()
    
    def save_changes(article_id, new_title, new_url, new_zendesk_id, dialog):
        try:
            logger.info("Updating article: %s", new_title)
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
            
            logger.info("Article updated successfully: %s", new_title)
            ui.notify('Article updated successfully!', type='positive')
            dialog.close()
            refresh_callback()
        except Exception as e:
            logger.error("Error updating article %s: %s", new_title, str(e))
            ui.notify(f'Error updating article: {str(e)}', type='negative')
    
    return handle_edit
