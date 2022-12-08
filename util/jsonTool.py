import os

import pyjson5 as json
from loguru import logger as l


def read_json(n: str) -> dict:
    try:
        with open(n, "r", encoding="utf-8") as load_f:
            load_dict = json.load(load_f)
        return load_dict
    except Exception as e:
        l.error(e)


def create_json(n: str, data: dict):
    with open(n, "wb") as f:
        json.dump(data, f)
