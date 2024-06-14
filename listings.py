import requests

import sys
import time

from loguru import logger as lg

sys.setrecursionlimit(10000)

url_main = "https://steamcommunity.com/market/search/render/"
#app_id = 2923300 #BANANA
#app_id = 578080 #PUBG
#app_id = 730 #CS2

@lg.catch()
def get_app_items(app_id):

    def get_items(start_page, count):
        time.sleep(10)
        payload = {
            "start" : int(start_page),
            "count" : int(count),
            "sort_column": "price",
            "sort_dir": "asc",
            "norender" : 1 #to get json
        }
        r = requests.get(url_main, params=payload)
        if r.status_code != 200:
            lg.warning(f"Got {r.status_code}")
            return get_items(start_page, count)
        try:
            answer_json = r.json()
        except Exception as e:
            lg.error(f"Some error in response.json")
            return None
        return answer_json
    first = get_items(0 , 78)
    lg.debug(f"First page: {first}")
    all_cellings = int(first["total_count"])
    lg.debug(f"All cellings: {all_cellings}")
    amount = 1
    apps = set()
    apps_id = set()
    with open(f"apps/{app_id}.txt", "w", encoding="utf-8") as file:
        for i in range((all_cellings + 99)//100):
            all_objects = get_items(i*100, 100)
            if all_objects:
                lg.warning(f"Got {len(all_objects['results'])} objects")
                for line in all_objects["results"]:
                    lg.debug(f"{line['app_name']}: {line['asset_description']['appid']}")
                    apps.add(line["app_name"])
                    apps_id.add(line['asset_description']['appid'])
                    lg.debug(f"{amount}. {line['name']}: {line['sell_price_text']} ({line['hash_name']})")
                    file.write(f"{amount}. {line['name']}: {line['sell_price_text']} ({line['hash_name']})")
                    file.write("\n")
                    amount += 1
                    if line['name'] != line['hash_name']:
                        lg.warning("name != hash_name")
            with open("apps.json", "w", encoding="utf-8") as file2:
                for app in apps:
                    file2.write(str(app))
                    file2.write("\n")

            with open("apps_id.json", "w", encoding="utf-8") as file2:
                for app_id in apps_id:
                    file2.write(str(app_id))
                    file2.write("\n")
    return apps, apps_id


def main():
    apps, apps_id = get_app_items(0)

    lg.info(f"Apps, that have items: {len(apps)}")
    lg.info(f"{apps}")
    with open("apps.json", "w", encoding="utf-8") as file:
        for app in apps:
            file.write(str(app))
            file.write("\n")

    with open("apps_id.json", "w", encoding="utf-8") as file:
        for app_id in apps_id:
            file.write(str(app_id))
            file.write("\n")



if __name__ == "__main__":
    lg.remove()
    lg.level("INFO", color="<green>")
    # lg.level("INFO", color="<cyan>")
    lg.add("debug.txt", format="{time} | {level} | {file} | {line} | {message}", level="DEBUG",
           rotation="100 MB",
           colorize=True, compression="zip")
    lg.add(sys.stdout,
           format="<level><b>{time} | {level} | {file} | {line} | {message}</b></level>",
           level="DEBUG",
           colorize=True)

    lg.info("Started parsing")
    main()