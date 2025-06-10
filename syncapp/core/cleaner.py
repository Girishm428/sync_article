from syncapp.loggers.log_cli import setup_logger

logger = setup_logger(__name__)
# ---------------------------- CONVERT TABS TO STATIC ----------------------------
def convert_tabs_to_static(soup, tab_container):
    """Converts a tabs UI block into static H3 headings and wraps tab content in <blockquote> for indentation."""

    logger.info("🔁 Converting a tabs-container section to static content")

    # Grab tab labels
    tabs = tab_container.select("ul.tabs > li")
    tab_titles = [tab.get_text(strip=True) for tab in tabs]
    logger.info(f"🔎 Tab titles found: {tab_titles}")

    # Grab tab content blocks (even hidden ones)
    all_panels = tab_container.select("div[role='tabpanel']")
    logger.info(f"📦 Total tab panels found: {len(all_panels)}")

    static_sections = []

    for title, panel in zip(tab_titles, all_panels):
        logger.info(f"🔍 Processing panel for tab: {title}, hidden={panel.has_attr('hidden')}")

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
        logger.info(f"📄 Added static section with blockquote for tab: {title}")

    if static_sections:
        tab_container.replace_with(*static_sections)
    else:
        logger.warning("⚠️ No matching tab content found. Tabs container skipped.")
