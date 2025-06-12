import json
from pathlib import Path
from syncapp.loggers.log_cli import setup_logger
import json
from pathlib import Path
from platformdirs import user_config_dir

#------------ logger ------------
logger = setup_logger(__name__)

# Set up application configuration directory
APP_NAME = "SyncImporter"
CONFIG_DIR = Path(user_config_dir(APP_NAME, appauthor=False))  # appauthor=False prevents duplicate folder
SETTINGS_FILE = CONFIG_DIR / "settings.json"

def ensure_settings_file():
    try:
        # First check if directory exists
        logger.info("Checking if directory exists: %s", CONFIG_DIR)
        if not CONFIG_DIR.exists():
            logger.info("Directory not found, creating: %s", CONFIG_DIR)
            try:
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                logger.info("Successfully created directory: %s", CONFIG_DIR)
            except Exception as e:
                logger.error("Failed to create directory: %s", str(e))
                raise
        else:
            logger.info("Directory already exists: %s", CONFIG_DIR)

        # Now check if settings file exists
        logger.info("Checking if settings file exists: %s", SETTINGS_FILE)
        if not SETTINGS_FILE.exists():
            logger.info("Settings file not found, creating new one at: %s", SETTINGS_FILE)
            default_settings = {
                "ZENDESK_DOMAIN": "",
                "EMAIL": "",
                "API_TOKEN": "",
                "LOCAL": "en-us"
            }
            try:
                with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(default_settings, f, indent=2)
                logger.info("Successfully created settings file at: %s", SETTINGS_FILE)
                logger.info("Settings file Resolve if any: %s", SETTINGS_FILE.resolve())
            except Exception as e:
                logger.error("Failed to create settings file: %s", str(e))
                raise
        else:
            logger.info("Settings file already exists at: %s", SETTINGS_FILE)
            logger.info("Settings file Resolve if any: %s", SETTINGS_FILE.resolve())
            # Verify we can read the file
            try:
                with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    json.load(f)
                logger.info("Successfully verified settings file is readable")
            except Exception as e:
                logger.error("Settings file exists but is not readable: %s", str(e))
                raise

        return SETTINGS_FILE
    except Exception as e:
        logger.error("Failed to create settings file in user config directory: %s", str(e))
        # Fallback to local directory if config directory is not accessible
        local_settings = Path(__file__).parent.parent / "webui" / "settings.json"
        logger.info("Attempting to use local settings file at: %s", local_settings)
        
        # Create webui directory if it doesn't exist
        if not local_settings.parent.exists():
            logger.info("Creating webui directory: %s", local_settings.parent)
            local_settings.parent.mkdir(parents=True, exist_ok=True)
        
        if not local_settings.exists():
            logger.info("Creating local settings file at %s", local_settings)
            default_settings = {
                "ZENDESK_DOMAIN": "",
                "EMAIL": "",
                "API_TOKEN": "",
                "LOCAL": "en-us"
            }
            with open(local_settings, 'w', encoding='utf-8') as f:
                json.dump(default_settings, f, indent=2)
            logger.info("Created local settings file at %s", local_settings)
        else:
            logger.info("Found existing local settings file at %s", local_settings)
            
        return local_settings

SETTINGS_FILE = ensure_settings_file()

logger.info("SETTINGS_FILE exists: %s", SETTINGS_FILE.exists())

def load_settings():
    try:
        logger.info("Loading settings from %s...", SETTINGS_FILE)
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        logger.error("Failed to load settings: %s", SETTINGS_FILE)
        return {}
    except Exception as e:
        logger.error("Error loading settings: %s", str(e))
        return {}

settings = load_settings()
logger.info("Settings loaded successfully")

ZENDESK_DOMAIN = settings.get("ZENDESK_DOMAIN", "")
logger.info("ZENDESK_DOMAIN: %s", ZENDESK_DOMAIN)

EMAIL = settings.get("EMAIL", "")
logger.info("EMAIL: %s", EMAIL)

API_TOKEN = settings.get("API_TOKEN", "")
masked_token = f"{API_TOKEN[:3]}****{API_TOKEN[-2:]}" if API_TOKEN else "(not set)"
logger.info("API_TOKEN: %s", masked_token)

LOCAL = settings.get("LOCAL", "en-us")
logger.info("LOCAL: %s", LOCAL)

def validate():
    logger.info("Validating started")
    # Load settings fresh
    current_settings = load_settings()
    
    # Check required fields
    required_fields = {
        "ZENDESK_DOMAIN": current_settings.get("ZENDESK_DOMAIN", ""),
        "EMAIL": current_settings.get("EMAIL", ""),
        "API_TOKEN": current_settings.get("API_TOKEN", ""),
        "LOCAL": current_settings.get("LOCAL", "en-us")
    }
    
    # Log the values we're checking
    for field, value in required_fields.items():
        masked_value = f"{value[:3]}****{value[-2:]}" if field == "API_TOKEN" and value else value
        logger.info("Checking %s: %s", field, masked_value)
    
    if not all(required_fields.values()):
        missing = [field for field, value in required_fields.items() if not value]
        logger.error("Missing required settings: %s", ", ".join(missing))
        raise EnvironmentError(f"Missing required settings: {', '.join(missing)}")
    
    logger.info("Settings validated successfully")

def save_settings_to_file(data):
    data = dict(data)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    logger.info("Settings saved to %s", SETTINGS_FILE)