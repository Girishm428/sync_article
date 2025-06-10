from syncapp.core.fetcher import fetch_content
from syncapp.core.zendesk import update_zendesk_translation, verify_article_update
from syncapp.config.settings import validate
from syncapp.loggers.log_ui import log_message

async def run_sync_process(source_url: str, article_id: str, title: str, settings: dict):
    try:
        await log_message("🔍 Validating settings...")
        validate()

        await log_message(f"🌐 Fetching content from: {source_url}")
        content = fetch_content(source_url)

        await log_message(f"✍️ Updating Zendesk article ID {article_id}...")
        update_zendesk_translation(
            article_id=article_id,
            zendesk_domain=settings["ZENDESK_DOMAIN"],
            locale=settings["LOCAL"],
            title=title,
            body_html=content,
        )

        await log_message("🔎 Verifying article update...")
        verify_article_update(article_id)

        await log_message("✅ Sync process completed successfully!")

    except Exception as e:
        await log_message(f"❌ Error during sync: {e}")
