from main import fetch_html

def test_fetch_html():
    url = "https://store.steampowered.com/search/?sort_by=Price_ASC&maxprice=free&supportedlang=english&hidef2p=1&ndl=1"
    html = fetch_html(url)
    assert "<html" in html.lower()