import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sys
import time

from loguru import logger as lg

def check_keyword(keyword, bad_words, string):
    for word in bad_words:
        if word in string:
            lg.warning(f"The word '{word}' in '{string}' is blocked")
            return False
    for word in keyword:
        if word not in string:
            lg.warning(f"The word '{word}' was not found in {string}")
            return False
    lg.info(f"The string '{string}' is good")
    return True

@lg.catch()
def main() -> None:
    sys.setrecursionlimit(3000)

    lg.remove()
    lg.level("INFO", color="<cyan>")
    lg.add("debug.txt", format="{time} | {level} | {file} | {line} | {message}", level="DEBUG",
           rotation="100 MB",
           colorize=True, compression="zip")
    lg.add(sys.stdout,
           format="<level><b>{time} | {level} | {file} | {line} | {message}</b></level>",
           level="DEBUG",
           colorize=True)

    lg.info("Started parsing")

    main_href = "https://steamcommunity.com/market/search?appid=2923300"
    keyword = ["market", "2923300"]
    bad_words = ["login"]

    visited = set()

    def parse(start_href: str, keyword: list, bad_words : list) -> None:
        lg.info(f"Parsing {start_href}")
        try:
            response = requests.get(start_href)
        except requests.exceptions.ConnectionError:
            lg.error(f"Connection Error to href {start_href}")
        except Exception as e:
            lg.error(f"Error: {e}")
            return None
        lg.info(f"{response.status_code}")
        with open("index.html", "w", encoding="utf-8") as file:
            file.write(response.text)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            lg.debug(f"Got soup for href {start_href}")
            tags = soup.find_all("a")
            urls = []
            for tag in tags:
                href = tag.get("href")
                if href is not None and href != "" and href != "#":
                    urls.append(href)
            lg.debug(f"Found {len(urls)}: {urls}")

            for url in urls:
                url_join = urljoin(start_href, url)
                if url_join not in visited:

                    if check_keyword(keyword, bad_words, url_join) and url_join.find("last_url") == -1:
                        visited.add(url_join)
                        parse(url_join, keyword, bad_words)


    parse(main_href, keyword, bad_words)

    with open(f"urls_app_{2923300}_.txt", "w", encoding="utf-8") as f:
        lg.info(f"Found {len(visited)} urls:")
        for url in visited:
            if "listings" in url:
                lg.info(f"{url}")
                f.write(f"{url}\n")




if __name__ == '__main__':
    main()
