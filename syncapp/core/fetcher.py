from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
from syncapp.core.cleaner import convert_tabs_to_static
from syncapp.utils.logger import setup_logger

logger = setup_logger(__name__)
# ---------------------------- FETCH AND CLEAN HTML CONTENT ----------------------------
def fetch_content(url):
    """Fetches the web page content and applies transformations for Zendesk formatting."""
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run without UI
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    logger.info(f"🌐 Fetching content from {url}")
    driver.get(url)
    time.sleep(3)  # Wait for dynamic content to render

    soup = BeautifulSoup(driver.page_source, "html.parser")
    main = soup.find('main')
    if not main:
        driver.quit()
        raise Exception("❌ Could not find <main> element.")

    content_div = main.find("div", class_="theme-doc-markdown")
    if not content_div:
        driver.quit()
        raise Exception("❌ Could not find markdown content block.")

    # 🧹 Remove copy buttons from code blocks
    for copy_button in content_div.select("button"):
        logger.info(f"🧹 Removing copy button with text: '{copy_button.text.strip()}'")
        copy_button.decompose()

    # 🧹 Remove images from info-type admonitions
    for admonition in content_div.find_all("div", class_=lambda c: c and "theme-admonition-info" in c):
        for img in admonition.find_all("img"):
            logger.info("🧹 Removing image from info admonition")
            img.decompose()

    # 🔁 Convert admonition heading to H2 and uppercase it
    for heading in content_div.find_all(class_=lambda c: c and "admonitionHeading" in c):
        heading_text = heading.get_text(strip=True).upper()
        new_heading = soup.new_tag("h2")
        new_heading.string = heading_text
        heading.replace_with(new_heading)
        logger.info(f"🔁 Converted admonition heading to H2: {heading_text}")

    # 🚫 Remove <h4> anchors with class starting with 'anchor anchorWithStickyNavbar'
    for h4 in content_div.find_all("h4", class_=lambda c: c and c.startswith("anchor anchorWithStickyNavbar")):
        logger.info("🧹 Removing <h4> anchor starting with 'anchor anchorWithStickyNavbar'")
        h4.decompose()

    # 🔄 Convert tab containers into static H3 + content
    for tab_container in content_div.find_all("div", class_=lambda c: c and "tabs-container" in c):
        convert_tabs_to_static(soup, tab_container)

    # 🔧 Normalize code blocks for Zendesk
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
            logger.info(f"🔧 Cleaned code block preview: {pre.get_text(strip=True)[:60]}...")

    # 🔁 Convert inline code <code> into <strong> (bold)
    for inline_code in content_div.find_all("code"):
        if inline_code.find_parent("pre") is None:
            strong_tag = soup.new_tag("strong")
            strong_tag.string = inline_code.get_text()
            inline_code.replace_with(strong_tag)
            logger.info(f"🔁 Converted inline code to <strong>: {strong_tag.string}")

    driver.quit()
    logger.info("✅ Content extracted and cleaned successfully.")
    return content_div.decode_contents()