import aiohttp
from syncapp.loggers.log_cli import setup_logger
from syncapp.config.settings import load_settings


logger = setup_logger(__name__)
# ---------------------------- ZENDESK UPDATE ----------------------------
async def update_zendesk_translation(article_id, zendesk_domain, locale, title, body_html):
    # Load fresh settings
    current_settings = load_settings()
    
    url = f"https://{zendesk_domain}/api/v2/help_center/articles/{article_id}/translations/{locale}.json"
    headers = {"Content-Type": "application/json"}
    payload = {
        "translation": {
            "title": title,
            "body": body_html
        }
    }
    logger.info("Updating Zendesk localized translation...")
    logger.info("URL: %s", url)
    logger.info("EMAIL: %s", current_settings.get('EMAIL', ''))
    logger.info("HEADERS: %s", headers)
    
    async with aiohttp.ClientSession() as session:
        async with session.put(
            url,
            auth=aiohttp.BasicAuth(current_settings.get('EMAIL', '') + "/token", current_settings.get('API_TOKEN', '')),
            headers=headers,
            json=payload
        ) as response:
            if response.status == 200:
                logger.info("Zendesk translation updated successfully!")
            else:
                logger.error("Failed to update translation. Status code: %d", response.status)
                error_text = await response.text()
                logger.error("Response: %s", error_text)
                response.raise_for_status()

# ---------------------------- VERIFICATION ----------------------------
async def verify_article_update(article_id, locale=None):
    # Load fresh settings
    current_settings = load_settings()
    
    # Use provided locale or default from settings
    if locale is None:
        locale = current_settings.get('LOCAL', 'en-us')
    
    url = f"https://{current_settings.get('ZENDESK_DOMAIN', '')}/api/v2/help_center/articles/{article_id}/translations/{locale}.json"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url,
            auth=aiohttp.BasicAuth(current_settings.get('EMAIL', '') + "/token", current_settings.get('API_TOKEN', ''))
        ) as response:
            if response.status == 200:
                data = await response.json()
                body = data.get('translation', {}).get('body')
                if body:
                    logger.info("Updated article preview (first 500 chars):")
                    logger.info("%s", body[:500])
                else:
                    logger.error("No body found in translation.")
            else:
                logger.error("Failed to fetch localized article. Status code: %d", response.status)
                error_text = await response.text()
                logger.error("Response text: %s", error_text)