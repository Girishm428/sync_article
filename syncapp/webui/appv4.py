from nicegui import ui
from pathlib import Path
import json
from syncapp.core.fetcher import fetch_content
from syncapp.core.zendesk import update_zendesk_translation, verify_article_update
from syncapp.config.settings import validate
from syncapp.utils.logger import setup_logger
from syncapp.utils.crypto import encrypt, decrypt


#------------ Settings ------------
SETTINGS_FILE = Path(__file__).parent / "settings.json"

# --- Load & Save Settings ---
def load_settings():
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
            if "API_TOKEN" in data and data["API_TOKEN"]:
                try:
                    data["API_TOKEN"] = decrypt(data["API_TOKEN"])
                except Exception:
                    data["API_TOKEN"] = ""
            return data
    return {"ZENDESK_DOMAIN": "", "EMAIL": "", "API_TOKEN": "", "LOCAL": "en-us"}

def save_settings_to_file(data):
    encrypted = dict(data)
    if encrypted.get("API_TOKEN"):
        encrypted["API_TOKEN"] = encrypt(encrypted["API_TOKEN"])
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(encrypted, f, indent=2)

settings = load_settings()

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

#------------Enhanced Settings Dialog ------------
with ui.dialog() as dialog, ui.card().classes('w-96 p-6'):
    ui.label('⚙️ Settings').classes('text-xl font-semibold mb-4 text-center')

    zendesk_domain = ui.input("Zendesk Domain", value=settings.get("ZENDESK_DOMAIN", "")).classes('mb-4').props('outlined')
    email = ui.input("Email", value=settings.get("EMAIL", "")).classes('mb-4').props('outlined')
    api_token = ui.input("API Token", value=settings.get("API_TOKEN", ""), password=True).classes('mb-4').props('outlined')
    locale = ui.input("Locale", value=settings.get("LOCAL", "en-us")).classes('mb-6').props('outlined')

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

#-----------Enhanced UI ------------
with ui.element('div').classes('absolute inset-0 flex items-center justify-center'):

    # 💎 Styled card
    with ui.card().classes(
        'bg-white w-full max-w-2xl p-8 rounded-2xl shadow-2xl'
    ):
        with ui.row().classes('justify-end mb-4'):
            ui.button('⚙️ Settings', on_click=dialog.open).props('flat color=gray')
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
        validate()
        content = fetch_content(source_url.value)
        update_zendesk_translation(article_id.value, settings["LOCAL"], title.value, content)
        verify_article_update(article_id.value)
        ui.notify("✅ Sync job completed.")
    except Exception as e:
        setup_logger("❌ Error during sync")
        ui.notify(f"❌ Sync failed: {e}", type="negative")

# --------- Start Web Server ---
if __name__ == "__main__":
    print("Requests imported successfully")
    print(f"Running {__file__} as __name__ = {__name__}")
    setup_logger("Starting web server on port 8000...")
    ui.run(host='0.0.0.0', port=8000, show=True, reload=False)

