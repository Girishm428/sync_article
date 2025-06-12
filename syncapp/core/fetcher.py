from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import asyncio
from syncapp.core.cleaner import convert_tabs_to_static
from syncapp.loggers.log_cli import setup_logger
import time

logger = setup_logger(__name__)
# ---------------------------- FETCH AND CLEAN HTML CONTENT ----------------------------
async def fetch_content(url):
    """Fetches the web page content and applies transformations for Zendesk formatting."""
    # Run Selenium in a separate thread to avoid blocking
    loop = asyncio.get_event_loop()
    content = await loop.run_in_executor(None, _fetch_content_sync, url)
    return content

def _fetch_content_sync(url):
    """Synchronous version of fetch_content that runs in a separate thread."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without UI
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        logger.info("Fetching content from %s", url)
        driver.get(url)
        logger.info("Waiting for page load...")
        time.sleep(3)  # Wait for dynamic content to render
        logger.info("Page loaded, getting source...")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        main = soup.find('main')
        if not main:
            raise Exception("Could not find <main> element.")

        logger.info("Found main element")
        content_div = main.find("div", class_="theme-doc-markdown")
        if not content_div:
            raise Exception("Could not find markdown content block.")

        logger.info("Found markdown content block")
        # Remove copy buttons from code blocks
        for copy_button in content_div.select("button"):
            logger.info("Removing copy button with text: '%s'", copy_button.text.strip())
            copy_button.decompose()

        # Remove images from info-type admonitions
        for admonition in content_div.find_all("div", class_=lambda c: c and "theme-admonition-info" in c):
            for img in admonition.find_all("img"):
                logger.info("Removing image from info admonition")
                img.decompose()

        # Convert admonition heading to H2 and uppercase it
        for heading in content_div.find_all(class_=lambda c: c and "admonitionHeading" in c):
            heading_text = heading.get_text(strip=True).upper()
            new_heading = soup.new_tag("h2")
            new_heading.string = heading_text
            heading.replace_with(new_heading)
            logger.info("Converted admonition heading to H2: %s", heading_text)

        # Remove <h4> anchors with class starting with 'anchor anchorWithStickyNavbar'
        for h4 in content_div.find_all("h4", class_=lambda c: c and c.startswith("anchor anchorWithStickyNavbar")):
            logger.info("Removing <h4> anchor starting with 'anchor anchorWithStickyNavbar'")
            h4.decompose()

        # Convert tab containers into static H3 + content
        for tab_container in content_div.find_all("div", class_=lambda c: c and "tabs-container" in c):
            logger.info("Converting tab containers into static H3 + content")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(convert_tabs_to_static(soup, tab_container))
            loop.close()

        # Normalize code blocks for Zendesk
        for code_wrapper in content_div.select("div[class*=codeBlock]"):
            pre = code_wrapper.find("pre")
            if pre:
                code = pre.find("code")
                if not code:
                    code = soup.new_tag("code")
                    code.string = pre.get_text()
                    pre.clear()
                    pre.append(code)
                pre.attrs.clear()
                code.attrs.clear()
                pre.replace_with(BeautifulSoup(str(pre), "html.parser"))
                logger.info("Cleaned code block preview: %s...", pre.get_text(strip=True)[:60])

        # Convert inline code <code> into <strong> (bold)
        for inline_code in content_div.find_all("code"):
            if inline_code.find_parent("pre") is None:
                strong_tag = soup.new_tag("strong")
                strong_tag.string = inline_code.get_text()
                inline_code.replace_with(strong_tag)
                logger.info("Converted inline code to <strong>: %s", strong_tag.string)

        logger.info("Content extracted and cleaned successfully.")
        content = content_div.decode_contents()
        logger.info("Final content length: %d", len(content))
        return content

    finally:
        driver.quit()