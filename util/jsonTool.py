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
    try:
        if os.path.exists(n):
            os.remove(n)
        with open(n, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception as e:
        l.error(e)
