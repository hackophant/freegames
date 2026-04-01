import requests
import sys
from bs4 import BeautifulSoup

ERROR_LIST_MARKERS_NOT_FOUND = "Could not find Steam list section markers"
ERROR_INVALID_GAME_LISTING = "Invalid game listing: missing <a> element"

STEAM_DEV_URL = "https://store.steampowered.com/search/?sort_by=Price_ASC&maxprice=free&supportedlang=english&hidef2p=1&ndl=1"
STEAM_PROD_URL = "https://store.steampowered.com/search/?sort_by=Price_ASC&maxprice=free&supportedlang=english&specials=1&hidef2p=1&ndl=1"
STEAM_LIST_START = "<!-- List Items -->"
STEAM_LIST_END = "<!-- End List Items -->"

def fetch_html(url: str) -> str:
    """
    Fetch HTML from platform store.
    Returns the HTML as a string
    Raises exception if request fails.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=10)
    # raise http-error for bad responses
    response.raise_for_status()

    return response.text


def extract_list_section(html: str, start:str, end: str) -> str:
    """
    Extract the section of the Steam search results between STEAM_LIST_START
    and STEAM_LIST_END and returns the section as a string.
    Raises ValueError if list markers not found.
    """
    start_index = html.find(start)
    end_index = html.find(end)

    if start_index == -1 or end_index == -1:
        raise ValueError(ERROR_LIST_MARKERS_NOT_FOUND)
    
    # move start_index to the end of start marker
    start_index += len(start)

    # return inner section slice
    return html[start_index:end_index].strip()


def extract_game_listing(section_html: str) -> dict:
    """
    Parse 
    """
    soup = BeautifulSoup(section_html, "html.parser")
    a = soup.find("a", class_="search_result_row")

    if not a:
        raise ValueError(ERROR_INVALID_GAME_LISTING)
    
    # app ID
    appid = a.get("data-ds-appid")
    # link
    link = a.get("href")
    # title
    title_tag = a.find("span", class_="title")
    title = title_tag.text.strip() if title_tag else None
    # platforms
    platform_tags = a.find_all("span", class_="platform_img")
    platforms = [tag.get("class")[1] for tag in platform_tags]
    # release date
    release_tag = a.find("div", class_="search_released")
    release_date = release_tag.text.strip() if release_tag else None
    # price
    price_block = a.find("div", class_="discount_final_price")
    final_price = release_tag.text.strip() if release_tag else None
    # original price
    original_block = a.find("div", class_="discount_original_price")
    original_price = original_block.text.strip() if original_block else None

    return {
        "appid": appid,
        "title": title,
        "link": link,
        "platforms": platforms,
        "release_date": release_date,
        "final_price": final_price,
        "original_price": original_price,
    }


def main():
    url = STEAM_PROD_URL
    markup = fetch_html(url)
    try:
        list_html = extract_list_section(markup, STEAM_LIST_START, STEAM_LIST_END)
    except ValueError as e:
        sys.exit(e)
    
    soup = BeautifulSoup(list_html, "html.parser")
    listings = soup.find_all("a", class_="search_result_row")
    games = [extract_game_listing(str(listing)) for listing in listings]

    for g in games:
        print(g["title"])


if __name__ == "__main__":
    main()
