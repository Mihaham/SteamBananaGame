import asyncio
import datetime
import os.path
import time

from multiprocessing import Process

import pandas
import requests
from loguru import logger as lg

from listings import get_app_items

APP_ID = 2923300  # BANANA
# APP_ID = 578080 #PUBG
# APP_ID = 730 #CS2

head = ["ITEM_ID", "Year", "Month", "Day", "Hours", "Minutes", "sec", "type", "quantity", "price", "time"]


@lg.catch()
def get_html(url: str) -> str:
    time.sleep(15)
    payload = {}
    response = requests.get(url)
    lg.debug(f"Status of {url}: {response.status_code}")
    return response.text


@lg.catch()
def get_item_id(url: str) -> int:
    text = get_html(url)
    for line in text.splitlines():
        if line.find("Market_LoadOrderSpread") != -1:
            id = int(line.split('(')[1].split(')')[0])
            lg.debug(f"Market id : {id}")
            return id
    return None


@lg.catch()
def get_activity(item_id: int, url="https://steamcommunity.com/market/itemordersactivity") -> list:
    payload = {
        "country": "RU",
        "language": "russian",
        "currency": 5,
        "norender": 1,
        "item_nameid": item_id
    }
    response = requests.get(url, params=payload)

    lg.debug(f"{item_id}. Status of {url}: {response}")
    return response.json()


@lg.catch()
def start_polling_app(app_id: int) -> None:
    if not os.path.exists(f"activity/activity_{app_id}.csv"):
        df = pandas.DataFrame(columns=head)
        df.to_csv(f"activity/activity_{app_id}.csv", index=False)

    #apps, apps_id, items = get_app_items(app_id)

    item_ids = []
    # for item in items:
    #     lg.debug(f"Item: {item}")
    #     url = f"https://steamcommunity.com/market/listings/{app_id}/{item['name']}"
    #     lg.info(f"url: {url}")
    #     new_id = get_item_id(url)
    #     if new_id is not None:
    #         item_ids.append(new_id)
    #     else:
    #         lg.warning(f"Returned None for {item['name']}")
    with open("cache.txt", "r", encoding="utf-8") as file:
        item_ids = list(map(int,file.readlines()))

    with open("cache2.txt", "w", encoding="utf-8") as f:
        for item_id in item_ids:
            f.write(f"{item_id}\n")

    lg.info(f"Number of items: {len(item_ids)}")
    lg.info(f"Ids: {item_ids}")

    proc = []
    for item_id in item_ids:
        if item_id is not None:
            p = Process(target=poll_item, args=(item_id, app_id))
            p.start()
            proc.append(p)
    for p in proc:
        p.join()


def poll_item(item_id, app_id):
    file = f"activity/activity_{app_id}_{item_id}.csv"
    if not os.path.exists(file):
        df = pandas.DataFrame(columns=head)
        df.to_csv(file, index=False)
    df = pandas.read_csv(file)
    while True:
        time.sleep(2)
        activity = get_activity(item_id)
        lg.debug(f"{item_id}: {activity}")
        time_now = datetime.datetime.now()

        for action in activity["activity"]:
            data = [item_id, time_now.year, time_now.month, time_now.day, time_now.hour,
                    time_now.minute, time_now.second, action['type'], action['quantity'],
                    action['price'],
                    action['time']]
            data = {a: [str(b)] for a, b in zip(head, data)}
            data = pandas.DataFrame(data)
            df = pandas.concat([df, data], ignore_index=True)
        df.to_csv(file, index=False)


def main() -> None:
    start_polling_app(APP_ID)


if __name__ == '__main__':
    main()
