import json
from loguru import logger as l
def ReadJson(n: str)->dict | str:
    try:
        with open(n, "r",encoding='utf-8') as load_f:
            load_dict = json.load(load_f)
        return load_dict
    except Exception as e: 
        l.error(e)



def CreateJson(n: str, data: dict):
    try:
        with open(n, "w",encoding='utf-8') as f:
            json.dump(data, f)
    except Exception as e: 
        l.error(e)