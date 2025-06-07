from config import settings
from utils.logger import setup_logger
from core.fetcher import fetch_content
from core.zendesk import update_zendesk_translation, verify_article_update

logger = setup_logger(__name__)

def main():
    try:
        settings.validate()
        content = fetch_content(settings.SOURCE_URL)
        update_zendesk_translation(settings.ARTICLE_ID, settings.LOCAL, settings.DST_TITLE, content)
        verify_article_update(settings.ARTICLE_ID)
    except Exception as e:
        logger.exception("❌ An error occurred")

if __name__ == "__main__":
    main()
