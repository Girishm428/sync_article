import requests
from syncapp.utils.logger import setup_logger
from syncapp.config import settings


logger = setup_logger(__name__)
# ---------------------------- ZENDESK UPDATE ----------------------------
def update_zendesk_translation(article_id, zendesk_domain, locale, title, body_html):
    url = f"https://{zendesk_domain}/api/v2/help_center/articles/{article_id}/translations/{locale}.json"
    headers = {"Content-Type": "application/json"}
    payload = {
        "translation": {
            "title": title,
            "body": body_html
        }
    }
    logger.info("📤 Updating Zendesk localized translation...")
    response = requests.put(url, auth=(settings.EMAIL + "/token", settings.API_TOKEN), headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("✅ Zendesk translation updated successfully!")
    else:
        logger.error(f"❌ Failed to update translation. Status code: {response.status_code}")
        logger.error("Response: %s", response.text)
        response.raise_for_status()

# ---------------------------- VERIFICATION ----------------------------
def verify_article_update(article_id, locale=settings.LOCAL):
    url = f"https://{settings.ZENDESK_DOMAIN}/api/v2/help_center/articles/{article_id}/translations/{locale}.json"
    response = requests.get(url, auth=(settings.EMAIL + "/token", settings.API_TOKEN))
    if response.status_code == 200:
        data = response.json()
        body = data.get('translation', {}).get('body')
        if body:
            logger.info("\n 🔍 Updated article preview (first 500 chars):")
            logger.info(body[:500])
        else:
            logger.error("No body found in translation.")
    else:
        logger.error(f"Failed to fetch localized article. Status code: {response.status_code}")
        logger.error("Response text:", response.text)
