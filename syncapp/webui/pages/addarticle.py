from nicegui import ui
import syncapp.config.database as db
from syncapp.webui.pages.header import header

# -----------------
# Page 1: Add Article
# -----------------
@ui.page('/')
def index_page():
    header()
    
    with ui.card().classes('w-full max-w-lg mx-auto mt-8'):
        ui.label('Add a New Article to Sync').classes('text-h6')
        
        title_input = ui.input('Article Title').props('outlined').classes('w-full')
        source_url_input = ui.input('Source Content URL').props('outlined').classes('w-full')
        zendesk_id_input = ui.input('Zendesk Article ID').props('outlined').classes('w-full')

        async def save_article():
            title = title_input.value
            url = source_url_input.value
            zid = zendesk_id_input.value

            if not all([title, url, zid]):
                ui.notify('All fields are required!', type='negative')
                return
            
            conn = db.get_db_connection()
            conn.execute(
                'INSERT INTO articles (title, source_url, article_id) VALUES (?, ?, ?)',
                (title, url, zid)
            )
            conn.commit()
            conn.close()
            
            ui.notify(f"Article '{title}' saved successfully!", type='positive')
            # Clear inputs
            title_input.value = ''
            source_url_input.value = ''
            zendesk_id_input.value = ''
            
            # Navigate to the list page to see the new entry
            # ui.open('/list')

        ui.button('Save Article', on_click=save_article).props('color=primary')

