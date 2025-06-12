from syncapp.loggers.log_cli import setup_logger
import asyncio

logger = setup_logger(__name__)
# ---------------------------- CONVERT TABS TO STATIC ----------------------------
async def convert_tabs_to_static(soup, tab_container):
    """Converts a tabs UI block into static H3 headings and wraps tab content in <blockquote> for indentation."""
    # Run the conversion in a separate thread since BeautifulSoup operations are CPU-bound
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _convert_tabs_to_static_sync, soup, tab_container)

def _convert_tabs_to_static_sync(soup, tab_container):
    """Synchronous version of convert_tabs_to_static that runs in a separate thread."""
    logger.info("Converting a tabs-container section to static content")

    # Grab tab labels
    tabs = tab_container.select("ul.tabs > li")
    tab_titles = [tab.get_text(strip=True) for tab in tabs]
    logger.info("Tab titles found: %s", tab_titles)

    # Grab tab content blocks (even hidden ones)
    all_panels = tab_container.select("div[role='tabpanel']")
    logger.info("Total tab panels found: %d", len(all_panels))

    static_sections = []

    for title, panel in zip(tab_titles, all_panels):
        logger.info("Processing panel for tab: %s, hidden=%s", title, panel.has_attr('hidden'))

        # Remove 'hidden' attribute to make content visible
        panel.attrs.pop("hidden", None)

        # Create H3 heading for tab title
        section_title = soup.new_tag("h3")
        section_title.string = title
        static_sections.append(section_title)

        # Wrap panel content inside blockquote for indentation
        blockquote = soup.new_tag("blockquote")
        # Move all children of panel into blockquote
        for child in list(panel.children):
            blockquote.append(child.extract())

        static_sections.append(blockquote)
        logger.info("Added static section with blockquote for tab: %s", title)

    if static_sections:
        tab_container.replace_with(*static_sections)
    else:
        logger.warning("No matching tab content found. Tabs container skipped.")
