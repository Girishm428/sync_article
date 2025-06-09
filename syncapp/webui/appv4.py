from nicegui import ui
import json
from syncapp.core.fetcher import fetch_content
from syncapp.core.zendesk import update_zendesk_translation, verify_article_update
from syncapp.config.settings import validate, ensure_settings_file
from syncapp.utils.logger import setup_logger

# from syncapp.utils.crypto import encrypt, decrypt
logger = setup_logger(__name__)

#------------ Settings ------------
SETTINGS_FILE = ensure_settings_file()

def load_settings():
    logger.info(f"🔍 searching for settings file {SETTINGS_FILE}...")
    logger.info(f"✅ SETTINGS_FILE exists: {SETTINGS_FILE.exists()}")
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                return data
    except Exception as e:
        logger.error(f"❌ Failed to load settings: {e}")
    return {"ZENDESK_DOMAIN": "", "EMAIL": "", "API_TOKEN": "", "LOCAL": "en-us"}

def save_settings_to_file(data):
    data = dict(data)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"✅ Settings saved to {SETTINGS_FILE}")

settings = load_settings()

# ------------ Reactive Settings Refs ------------

# 🔧 Global style for full height and gray background
ui.add_head_html('''
    <style>
        html, body, #app {
            height: 100%;
            width: 100%;
            margin: 0;
            padding: 0;
            background-color: #f3f4f6; /* Tailwind's bg-gray-100 */
            display: flex;
            align-items: center;
            justify-content: center;
        }
    </style>
''')

def show_settings_dialog():
    current_settings = load_settings()
    with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
        ui.label('⚙️ Settings').classes('text-xl font-semibold mb-4 text-center')

        zendesk_domain = ui.input("Zendesk Domain", value=current_settings.get("ZENDESK_DOMAIN", "")).classes('mb-4').props('outlined')
        email = ui.input("Email", value=current_settings.get("EMAIL", "")).classes('mb-4').props('outlined')
        api_token = ui.input("API Token", value=current_settings.get("API_TOKEN", ""), password=True).classes('mb-4').props('outlined')
        locale = ui.input("Locale", value=current_settings.get("LOCAL", "en-us")).classes('mb-6').props('outlined')

        def save_settings():
            settings.update({
                "ZENDESK_DOMAIN": zendesk_domain.value,
                "EMAIL": email.value,
                "API_TOKEN": api_token.value,
                "LOCAL": locale.value,
            })
            save_settings_to_file(settings)
            ui.notify("✅ Settings saved.")
            dialog.close()

        with ui.row().classes('justify-end gap-4'):
            ui.button("💾 Save", on_click=save_settings).props('color=primary')
            ui.button("❌ Close", on_click=dialog.close).props('flat color=gray')
    
    dialog.open()

#-----------Enhanced UI ------------
with ui.element('div').classes('absolute inset-0 flex items-center justify-center'):

    # 💎 Styled card
    with ui.card().classes(
        'bg-white w-full max-w-2xl p-8 rounded-2xl shadow-2xl'
    ):
        with ui.row().classes('justify-end mb-4'):
            ui.button('⚙️ Settings', on_click=show_settings_dialog).props('flat color=gray')
        ui.label('📄 Import Article to Zendesk').classes(
            'text-3xl font-bold mb-6 text-center text-blue-700'
        )

        input_style = 'text-lg py-4'

        source_url = ui.input('Source URL', placeholder='Enter source URL') \
            .props(f'outlined input-class={input_style}').classes('w-full mb-5')

        article_id = ui.input('Destination Article ID', placeholder='Enter destination article ID') \
            .props(f'outlined input-class={input_style}').classes('w-full mb-5')

        title = ui.input('Article Title', placeholder='Enter article title') \
            .props(f'outlined input-class={input_style}').classes('w-full mb-7')

        with ui.row().classes('justify-end'):
            ui.button("🚀 Submit", on_click=lambda: start_sync()).props('color=primary size=lg')

          

#------------ Sync Logic ------------
def start_sync():
    try:
        logger.info(f"🔍 Validating settings...")   
        validate()
                
        logger.info(f"🔍 Fetching content from {source_url.value}...")
        content = fetch_content(source_url.value)
        
        logger.info(f"🔍 Updating Zendesk translation for article {article_id.value}...")
        update_zendesk_translation(article_id.value, settings["ZENDESK_DOMAIN"], settings["LOCAL"], title.value, content)
        
        logger.info(f"🔍 Verifying article update for {article_id.value}...")
        verify_article_update(article_id.value)

        logger.info("✅ Sync job completed.")
    except Exception as e:
        logger.error(f"❌ Error during sync: {e}")
        ui.notify(f"❌ Sync failed: {e}", type="negative")

# --------- Start Web Server ---
if __name__ == "__main__":
    logger.info("Requests imported successfully")
    logger.info(f"Running {__file__} as __name__ = {__name__}")
    logger.info("Starting web server on port 8000...")
    ui.run(host='0.0.0.0', port=8000, show=True, reload=False)

