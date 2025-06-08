import json
from pathlib import Path
from syncapp.utils.logger import setup_logger

logger = setup_logger(__name__)

SETTINGS_FILE = Path(__file__).parent.parent / "webui" / "settings.json"
logger.info(f"✅ SETTINGS_FILE exists: {SETTINGS_FILE.exists()}")

def load_settings():
    logger.info(f"🔍 Loading settings from {SETTINGS_FILE}...")
    if SETTINGS_FILE.exists():
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    logger.error(f"❌ Failed to load settings: {SETTINGS_FILE}")
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
    if not all([ZENDESK_DOMAIN, EMAIL, API_TOKEN, LOCAL]):
        logger.error("❌ Missing one or more required settings in settings.json.")
        raise EnvironmentError("❌ Missing one or more required settings in settings.json.")
    logger.info("✅ Settings validated successfully.")
