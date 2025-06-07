# syncapp/webui/main.py
from nicegui import ui
from fastapi import Request
from pathlib import Path
import json
import os


SETTINGS_FILE = Path(__file__).resolve().parent.parent / "settings.json"

# Global state
source_url = ui.input("Source URL", placeholder="Enter source URL")
article_id = ui.input("Destination Article ID", placeholder="Enter destination article ID")
article_title = ui.input("Article Title", placeholder="Enter article title")

with ui.row():
    def open_settings():
        dialog.open()

    ui.button("⚙️ Settings", on_click=open_settings)
    ui.button("🚀 Submit", on_click=lambda: sync())

# Settings dialog
dialog = ui.dialog()
with dialog:
    with ui.card():
        zendesk_domain = ui.input("Zendesk Domain")
        email = ui.input("Email")
        api_token = ui.input("API Token", password=True)
        locale = ui.input("Locale", value="en-us")

        def save_settings():
            data = {
                "ZENDESK_DOMAIN": zendesk_domain.value,
                "EMAIL": email.value,
                "API_TOKEN": api_token.value,
                "LOCAL": locale.value
            }
            with open(SETTINGS_FILE, "w") as f:
                json.dump(data, f, indent=2)
            ui.notify("✅ Settings saved")

        ui.button("💾 Save", on_click=save_settings)

# Load saved settings (if any)
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r") as f:
        saved = json.load(f)
        zendesk_domain.value = saved.get("ZENDESK_DOMAIN", "")
        email.value = saved.get("EMAIL", "")
        api_token.value = saved.get("API_TOKEN", "")
        locale.value = saved.get("LOCAL", "en-us")

# Backend sync logic
def sync():
    try:
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)

        # 👇 Call your existing sync logic from here
        from syncapp.core.fetcher import fetch_content
        from syncapp.core.zendesk import update_zendesk_translation, verify_article_update
        from syncapp.config.settings import validate

        # You may override config here if needed
        validate()  # optional

        content = fetch_content(source_url.value)
        update_zendesk_translation(
            article_id.value,
            settings["LOCAL"],
            article_title.value,
            content
        )
        verify_article_update(article_id.value)

        ui.notify("✅ Sync completed successfully")
    except Exception as e:
        print(f"❌ Error: {e}")
        ui.notify(f"❌ Sync failed: {str(e)}")

ui.run(port=8000, title="OpenZiti → Zendesk Sync")
