import syncapp.config.database as db
from nicegui import ui


def create_delete_handler(art, refresh_callback):
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
            refresh_callback()
        except Exception as e:
            ui.notify(f'Error deleting article: {str(e)}', type='negative')
    
    return handle_delete

def create_bulk_delete_handler(selected_articles, refresh_callback):
    """
    Creates a bulk delete handler for multiple articles.
    
    Args:
        selected_articles (set): Set of selected article IDs
        refresh_callback (callable): Function to refresh the UI after deletion
    """
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
            refresh_callback()
        except Exception as e:
            ui.notify(f'Error deleting articles: {str(e)}', type='negative')
    
    return handle_bulk_delete

