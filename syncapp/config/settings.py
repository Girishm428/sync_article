import json
from pathlib import Path
from syncapp.utils.logger import setup_logger
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
        logger.info(f"Checking if directory exists: {CONFIG_DIR}")
        if not CONFIG_DIR.exists():
            logger.info(f"Directory not found, creating: {CONFIG_DIR}")
            try:
                CONFIG_DIR.mkdir(parents=True, exist_ok=True)
                logger.info(f"Successfully created directory: {CONFIG_DIR}")
            except Exception as e:
                logger.error(f"Failed to create directory: {e}")
                raise
        else:
            logger.info(f"Directory already exists: {CONFIG_DIR}")

        # Now check if settings file exists
        logger.info(f"Checking if settings file exists: {SETTINGS_FILE}")
        if not SETTINGS_FILE.exists():
            logger.info(f"Settings file not found, creating new one at: {SETTINGS_FILE}")
            default_settings = {
                "ZENDESK_DOMAIN": "",
                "EMAIL": "",
                "API_TOKEN": "",
                "LOCAL": "en-us"
            }
            try:
                with open(SETTINGS_FILE, 'w') as f:
                    json.dump(default_settings, f, indent=2)
                logger.info(f"Successfully created settings file at: {SETTINGS_FILE}")
            except Exception as e:
                logger.error(f"Failed to create settings file: {e}")
                raise
        else:
            logger.info(f"Settings file already exists at: {SETTINGS_FILE}")
            # Verify we can read the file
            try:
                with open(SETTINGS_FILE, 'r') as f:
                    json.load(f)
                logger.info("Successfully verified settings file is readable")
            except Exception as e:
                logger.error(f"Settings file exists but is not readable: {e}")
                raise

        return SETTINGS_FILE
    except Exception as e:
        logger.error(f"Failed to create settings file in user config directory: {e}")
        # Fallback to local directory if config directory is not accessible
        local_settings = Path(__file__).parent.parent / "webui" / "settings.json"
        logger.info(f"Attempting to use local settings file at: {local_settings}")
        
        # Create webui directory if it doesn't exist
        if not local_settings.parent.exists():
            logger.info(f"Creating webui directory: {local_settings.parent}")
            local_settings.parent.mkdir(parents=True, exist_ok=True)
        
        if not local_settings.exists():
            logger.info(f"Creating local settings file at {local_settings}")
            default_settings = {
                "ZENDESK_DOMAIN": "",
                "EMAIL": "",
                "API_TOKEN": "",
                "LOCAL": "en-us"
            }
            with open(local_settings, 'w') as f:
                json.dump(default_settings, f, indent=2)
            logger.info(f"Created local settings file at {local_settings}")
        else:
            logger.info(f"Found existing local settings file at {local_settings}")
            
        return local_settings

SETTINGS_FILE = ensure_settings_file()


logger.info(f"🔍 Using settings file: {SETTINGS_FILE}")
logger.info(f"🔍 Using settings file Resolve if any: {SETTINGS_FILE.resolve()}")
logger.info(f"✅ SETTINGS_FILE exists: {SETTINGS_FILE.exists()}")

def load_settings():
    try:
        logger.info(f"🔍 Loading settings from {SETTINGS_FILE}...")
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        logger.error(f"❌ Failed to load settings: {SETTINGS_FILE}")
        return {}
    except Exception as e:
        logger.error(f"❌ Error loading settings: {e}")
        return {}

settings = load_settings()
logger.info(f"✅ Settings loaded")

ZENDESK_DOMAIN = settings.get("ZENDESK_DOMAIN", "")
logger.info(f"✅ ZENDESK_DOMAIN: {ZENDESK_DOMAIN}")

ARTICLE_ID = settings.get("ZENDESK_ARTICLE_ID", "")
logger.info(f"✅ ARTICLE_ID: {ARTICLE_ID}")

EMAIL = settings.get("EMAIL", "")
logger.info(f"✅ EMAIL: {EMAIL}")

API_TOKEN = settings.get("API_TOKEN", "")
masked_token = f"{API_TOKEN[:3]}****{API_TOKEN[-2:]}" if API_TOKEN else "(not set)"
logger.info(f"✅ API_TOKEN: {masked_token}")

SOURCE_URL = settings.get("OPENZITI_SOURCE_URL", "")
logger.info(f"✅ SOURCE_URL: {SOURCE_URL}")

LOCAL = settings.get("LOCAL", "en-us")
logger.info(f"✅ LOCAL: {LOCAL}")

DST_TITLE = settings.get("DST_TITLE", "")
logger.info(f"✅ DST_TITLE: {DST_TITLE}")

def validate():
    logger.info(f"🔍 Validating started")
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
        logger.info(f"Checking {field}: {masked_value}")
    
    if not all(required_fields.values()):
        missing = [field for field, value in required_fields.items() if not value]
        logger.error(f"❌ Missing required settings: {', '.join(missing)}")
        raise EnvironmentError(f"❌ Missing required settings: {', '.join(missing)}")
    
    logger.info("✅ Settings validated successfully.")
