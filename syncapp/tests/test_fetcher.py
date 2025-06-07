from bs4 import BeautifulSoup
from core.fetcher import convert_tabs_to_static

def test_convert_tabs_to_static_basic():
    html = '''
    <div class="tabs-container">
        <ul class="tabs">
            <li>Tab1</li><li>Tab2</li>
        </ul>
        <div role="tabpanel" hidden><p>Content 1</p></div>
        <div role="tabpanel" hidden><p>Content 2</p></div>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    tab_container = soup.find("div", class_="tabs-container")

    convert_tabs_to_static(soup, tab_container)

    # Assert tabs container is replaced
    assert soup.find("div", class_="tabs-container") is None

    h3_titles = [h3.get_text() for h3 in soup.find_all("h3")]
    assert h3_titles == ["Tab1", "Tab2"]

    blockquotes = soup.find_all("blockquote")
    assert len(blockquotes) == 2
    assert blockquotes[0].get_text(strip=True) == "Content 1"
    assert blockquotes[1].get_text(strip=True) == "Content 2"
