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