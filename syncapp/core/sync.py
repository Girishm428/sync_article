# syncapp/core/sync.py
from syncapp.config import settings
from syncapp.core.fetcher import fetch_content
from syncapp.core.zendesk import update_zendesk_translation, verify_article_update
from syncapp.config.settings import validate

def run_sync(source_url: str, article_id: str, title: str, user_settings: dict):
    # Optionally override global settings with user_settings if needed
    validate()  # Or adjust this to accept overrides
    content = fetch_content(source_url)
    update_zendesk_translation(article_id, user_settings.get("LOCAL", "en-us"), title, content)
    verify_article_update(article_id)
