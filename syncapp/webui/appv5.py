from nicegui import ui
from syncapp.webui.pages.addarticle import index_page
from syncapp.webui.pages.listarticle import list_page
from syncapp.webui.pages.settingspage import settings_page
from syncapp.webui.pages.log_viewer import log_viewer_page
from syncapp.loggers.log_cli import setup_logger
from syncapp.config.database import init_db
from syncapp.backend.sync_auto_run import run_scheduler, stop_scheduler

logger = setup_logger(__name__)

def initialize_application():
    """Initialize all application components."""
    try:
        # Initialize database
        logger.info("Initializing database...")
        init_db()
        
        # Start scheduler
        logger.info("Starting scheduler...")
        run_scheduler()
        logger.info("Application initialization completed successfully")
        
    except Exception as e:
        logger.error("Error during application initialization: %s", str(e))
        raise

# Initialize application components
initialize_application()

@ui.page('/')
def main():
    index_page()

@ui.page('/items')
def show_items():
    list_page()

@ui.page('/settings')
def show_settings():
    settings_page()

@ui.page('/logs')
def show_logs():
    log_viewer_page()

# --------- Start Web Server ---
if __name__ == "__main__":
    try:
        logger.info("Requests imported successfully")
        logger.info("Running %s as __name__ = %s", __file__, __name__)
        logger.info("Starting web server on port 8000...")
        ui.run(host='0.0.0.0', port=8000, show=True, reload=False)
    except Exception as e:
        logger.error("Error starting web server: %s", str(e))
        # Ensure scheduler is stopped if application fails to start
        stop_scheduler()
        raise  