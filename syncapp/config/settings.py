import os
from dotenv import load_dotenv

load_dotenv()

# ZENDESK_DOMAIN = os.getenv("ZENDESK_DOMAIN")
# ARTICLE_ID = os.getenv("ZENDESK_ARTICLE_ID")
# EMAIL = os.getenv("ZENDESK_EMAIL")
# API_TOKEN = os.getenv("ZENDESK_API_TOKEN")
# SOURCE_URL = os.getenv("OPENZITI_SOURCE_URL")
# LOCAL = os.getenv("ZENDESK_LOCAL")
# DST_TITLE = os.getenv("ZENDESK_DST_TITLE")

ZENDESK_DOMAIN = os.environ["ZENDESK_DOMAIN"]
ARTICLE_ID = os.environ["ZENDESK_ARTICLE_ID"]
EMAIL = os.environ["ZENDESK_EMAIL"]
API_TOKEN = os.environ["ZENDESK_API_TOKEN"]
SOURCE_URL = os.environ["OPENZITI_SOURCE_URL"]
LOCAL = os.environ["ZENDESK_LOCAL"]
DST_TITLE = os.environ["ZENDESK_DST_TITLE"]



def validate():
    if not all([ZENDESK_DOMAIN, ARTICLE_ID, EMAIL, API_TOKEN, SOURCE_URL, LOCAL, DST_TITLE]):
        raise EnvironmentError("❌ Missing one or more required environment variables.")
