from syncapp.config.settings import ensure_settings_file, load_settings
from syncapp.loggers.log_cli import setup_logger
from syncapp.core.fetcher import fetch_content
from syncapp.core.zendesk import update_zendesk_translation, verify_article_update
from syncapp.config.settings import validate


logger = setup_logger(__name__)

# Load environment variables from .env file
#------------ Settings ------------
SETTINGS_FILE = ensure_settings_file()

load_settings()

settings = load_settings()

async def run_sync_async(article_id: str, source_url: str, title: str):
    """
    Async wrapper for the sync logic to be used with NiceGUI without blocking the UI.
    """
    try:
        logger.info("🔍 Validating settings...")
        validate()

        logger.info(f"🌐 Fetching content from: {source_url}")
        content = fetch_content(source_url)

        logger.info(f"✍️ Updating Zendesk article ID {article_id}...")
        update_zendesk_translation(
            article_id=article_id,
            zendesk_domain=settings["ZENDESK_DOMAIN"],
            locale=settings["LOCAL"],
            title=title,
            body_html=content,
        )

        logger.info("🔎 Verifying article update...")
        verify_article_update(article_id)

        logger.info("✅ Sync process completed successfully!")

    except Exception as e:
        logger.info(f"❌ Error during sync: {e}")
    return True, "Sync process completed successfully!"