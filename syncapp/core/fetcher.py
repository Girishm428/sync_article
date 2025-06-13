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

def load_page(driver, url):
    logger.info("Fetching content from %s", url)
    driver.get(url)
    logger.info("Waiting for page load...")
    time.sleep(3)
    logger.info("Page loaded, getting source...")
    return driver.page_source

def find_main_element(soup):
    main = soup.find('main')
    if not main:
        raise Exception("Could not find <main> element.")
    logger.info("Found main element")
    return main

def find_markdown_content(main):
    content_div = main.find("div", class_="theme-doc-markdown")
    if not content_div:
        raise Exception("Could not find markdown content block.")
    logger.info("Found markdown content block")
    return content_div

def remove_copy_buttons(content_div):
    for copy_button in content_div.select("button"):
        logger.info("Removing copy button with text: '%s'", copy_button.text.strip())
        copy_button.decompose()

def remove_images_from_info_admonitions(content_div):
    for admonition in content_div.find_all("div", class_=lambda c: c and "theme-admonition-info" in c):
        for img in admonition.find_all("img"):
            logger.info("Removing image from info admonition")
            img.decompose()

def convert_admonition_heading_to_h2(soup, content_div):
    for heading in content_div.find_all(class_=lambda c: c and "admonitionHeading" in c):
        heading_text = heading.get_text(strip=True).upper()
        new_heading = soup.new_tag("h2")
        new_heading.string = heading_text
        heading.replace_with(new_heading)
        logger.info("Converted admonition heading to H2: %s", heading_text)

def remove_h4_anchors_with_sticky_navbar(content_div):
    for h4 in content_div.find_all("h4", class_=lambda c: c and c.startswith("anchor anchorWithStickyNavbar")):
        logger.info("Removing <h4> anchor starting with 'anchor anchorWithStickyNavbar'")
        h4.decompose()

def convert_tab_containers_to_static(soup, content_div):
    for tab_container in content_div.find_all("div", class_=lambda c: c and "tabs-container" in c):
        logger.info("Converting tab containers into static H3 + content")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(convert_tabs_to_static(soup, tab_container))
        loop.close()

def normalize_code_blocks(soup, content_div):
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

def convert_inline_code_to_strong(soup, content_div):
    for inline_code in content_div.find_all("code"):
        if inline_code.find_parent("pre") is None:
            strong_tag = soup.new_tag("strong")
            strong_tag.string = inline_code.get_text()
            inline_code.replace_with(strong_tag)
            logger.info("Converted inline code to <strong>: %s", strong_tag.string)

def _fetch_content_sync(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    try:
        page_source = load_page(driver, url)
        soup = BeautifulSoup(page_source, "html.parser")
        main = find_main_element(soup)
        content_div = find_markdown_content(main)
        remove_copy_buttons(content_div)
        remove_images_from_info_admonitions(content_div)
        convert_admonition_heading_to_h2(soup, content_div)
        remove_h4_anchors_with_sticky_navbar(content_div)
        convert_tab_containers_to_static(soup, content_div)
        normalize_code_blocks(soup, content_div)
        convert_inline_code_to_strong(soup, content_div)
        content = content_div.decode_contents()
        logger.info("Final content length: %d", len(content))
        return content
    finally:
        driver.quit()