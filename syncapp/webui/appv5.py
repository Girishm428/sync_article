from nicegui import ui
from syncapp.webui.pages.addarticle import index_page
from syncapp.webui.pages.listarticle import list_page
from syncapp.webui.pages.settingspage import settings_page
from syncapp.loggers.log_cli import setup_logger
from syncapp.config.database import init_db

logger = setup_logger(__name__)

init_db()

@ui.page('/')
def main():
    index_page()

@ui.page('/items')
def show_items():
    list_page()

@ui.page('/settings')
def show_settings():
    settings_page()

# --------- Start Web Server ---
if __name__ == "__main__":
    logger.info("Requests imported successfully")
    logger.info(f"Running {__file__} as __name__ = {__name__}")
    logger.info("Starting web server on port 8000...")
    ui.run(host='0.0.0.0', port=8000, show=True, reload=False)  