import typer
from syncapp.config import settings
from syncapp.utils.logger import setup_logger
from syncapp.core.fetcher import fetch_content
from syncapp.core.zendesk import update_zendesk_translation, verify_article_update
from syncapp.config.settings import validate

logger = setup_logger(__name__)
app = typer.Typer()

@app.command()
def sync():
    try:
        validate()
        content = fetch_content(settings.SOURCE_URL)
        update_zendesk_translation(settings.ARTICLE_ID, settings.LOCAL, settings.DST_TITLE, content)
        verify_article_update(settings.ARTICLE_ID)
        print(app.registered_commands)
    except Exception as e:
        logger.exception("❌ An error occurred")

if __name__ == "__main__":
    app()
