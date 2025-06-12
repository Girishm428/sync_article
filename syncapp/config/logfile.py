from pathlib import Path
from platformdirs import user_config_dir


#------------ Database ------------


def create_log_file():
    # Create logs directory if it doesn't exist
    APP_NAME = "SyncImporter"
    CONFIG_DIR = Path(user_config_dir(APP_NAME, appauthor=False))  # appauthor=False prevents duplicate folder
    LOG_FILE = CONFIG_DIR / "syncapp.log"

    return LOG_FILE