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

        # Load fresh settings
        current_settings = load_settings()
        
        # Validate required settings
        if not current_settings.get("ZENDESK_DOMAIN"):
            raise ValueError("Zendesk domain is not set in settings")
        if not current_settings.get("EMAIL"):
            raise ValueError("Email is not set in settings")
        if not current_settings.get("API_TOKEN"):
            raise ValueError("API token is not set in settings")

        logger.info(f"🌐 Fetching content from: {source_url}")
        content = await fetch_content(source_url)

        logger.info(f"✍️ Updating Zendesk article ID {article_id}...")
        await update_zendesk_translation(
            article_id=article_id,
            zendesk_domain=current_settings["ZENDESK_DOMAIN"],
            locale=current_settings["LOCAL"],
            title=title,
            body_html=content,
        )

        logger.info("🔎 Verifying article update...")
        await verify_article_update(article_id)

        logger.info("✅ Sync process completed successfully!")
        return True, "Sync process completed successfully!"

    except Exception as e:
        error_msg = str(e)
        logger.error(f"❌ Error during sync: {error_msg}")
        return False, f"Sync failed: {error_msg}"