import pyjson5 as json
import loguru


def read_json(n: str) -> dict:
    try:
        with open(n, "r", encoding="utf-8") as load_f:
            load_dict = json.load(load_f)
        return load_dict
    except Exception as e:
        loguru.logger.error(e)


def create_json(n: str, data: dict):
    with open(n, "wb") as f:
        json.dump(data, f)
