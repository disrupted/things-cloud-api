from __future__ import annotations

import json
import random
import string
from datetime import date, datetime, timedelta, timezone

import requests
from loguru import logger
from requests.exceptions import RequestException

from settings import ACCOUNT, USER_AGENT

API_BASE = "https://cloud.culturedcode.com/version/1"

headers = {
    "Accept": "application/json",
    "Accept-Charset": "UTF-8",
    "Accept-Language": "en-gb",
    "Host": "cloud.culturedcode.com",
    "User-Agent": USER_AGENT,
}


def get_timestamp() -> float:
    return datetime.now().timestamp()


def today() -> datetime:
    tz_local = datetime.now(timezone.utc).astimezone().tzinfo
    return datetime.combine(date.today(), datetime.min.time(), tz_local)


def offset_date(dt: datetime, days: int) -> datetime:
    return dt + timedelta(days=days)


def as_timestamp(dt: datetime) -> int:
    return int(dt.replace(tzinfo=timezone.utc).timestamp())


def create_random_string(len: int = 22) -> str:
    return "".join(random.choices(string.ascii_letters, k=len))


def get_current_index(index: int) -> int | None:
    try:
        response = requests.get(
            url=f"{API_BASE}/history/{ACCOUNT}/items",
            params={
                "start-index": str(index),
            },
            headers=headers,
        )
        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Body: {response.content}")
        if response.status_code == 200:
            return response.json()["current-item-index"]
        else:
            logger.error("Error getting current index", response.content)
    except RequestException as e:
        logger.error("HTTP Request failed", e)


def create(
    index: int,
    title: str,
    scheduled_date: datetime | None = None,
    due_date: datetime | None = None,
) -> int | None:
    now = get_timestamp()
    uuid = create_random_string()

    try:
        response = requests.post(
            url=f"{API_BASE}/history/{ACCOUNT}/commit",
            params={
                "ancestor-index": str(index),
                "_cnt": "1",
            },
            headers={
                **headers,
                "Schema": "301",
                "Content-Type": "application/json; charset=UTF-8",
                "App-Id": "com.culturedcode.ThingsMac",
                "Push-Priority": "5",
                "App-Instance-Id": "-com.culturedcode.ThingsMac",
            },
            data=json.dumps(
                {
                    uuid: {
                        "t": 0,
                        "e": "Task6",
                        "p": {
                            "tp": 0,
                            "sr": as_timestamp(scheduled_date)
                            if scheduled_date
                            else None,
                            "dds": None,
                            "rt": [],
                            "rmd": None,
                            "ss": 0,
                            "tr": False,  # in_trash
                            "dl": [],
                            "icp": False,  # is_project
                            "st": 0,  # status: {0: inbox, 1: today/anytime}
                            "ar": [],
                            "tt": title,
                            "do": 0,
                            "lai": None,
                            "tir": as_timestamp(scheduled_date)
                            if scheduled_date
                            else None,
                            "tg": [],
                            "agr": [],
                            "ix": -35483,
                            "cd": now,  # creation_date
                            "lt": False,
                            "icc": 0,
                            "ti": -454,
                            "md": now,  # modification_date
                            "dd": as_timestamp(due_date) if due_date else None,
                            "ato": None,
                            "nt": {"_t": "tx", "ch": 0, "v": "", "t": 1},  # note
                            "icsd": None,
                            "pr": [],
                            "rp": None,
                            "acrd": None,
                            "sp": None,
                            "sb": 0,
                            "rr": None,
                        },
                    }
                }
            ),
        )
        logger.debug(f"Status: {response.status_code}")
        logger.debug(f"Body: {response.content}")
        if response.status_code == 200:
            return response.json()["server-head-index"]
        else:
            logger.error("Error creating new item", response.content)
    except RequestException as e:
        logger.error("HTTP Request failed", e)


if __name__ == "__main__":
    index = get_current_index(1540)
    logger.debug(f"current index: {index}")
    due_date = today() + timedelta(days=2)
    if index is not None:
        new_index = create(
            index,
            "HELLO WORLD",
            due_date=due_date,
        )
        logger.debug(f"new index: {new_index}")
