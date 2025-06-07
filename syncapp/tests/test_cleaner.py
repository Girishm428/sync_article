from bs4 import BeautifulSoup
from core.cleaner import clean_admonitions, remove_copy_buttons

def test_remove_copy_buttons():
    html = '''
    <div class="theme-doc-markdown">
        <button>Copy</button>
        <button>Copy</button>
        <p>Some content</p>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    container = soup.find("div", class_="theme-doc-markdown")

    remove_copy_buttons(container)
    assert len(container.find_all("button")) == 0
    assert container.find("p") is not None

def test_clean_admonitions():
    html = '''
    <div class="theme-admonition-info">
        <img src="image.png"/>
        <p>Info text</p>
    </div>
    '''
    soup = BeautifulSoup(html, "html.parser")
    admonition = soup.find("div", class_="theme-admonition-info")

    clean_admonitions(admonition)
    assert admonition.find("img") is None
    assert admonition.find("p") is not None
