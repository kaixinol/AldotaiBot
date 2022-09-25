from jsonTool import *
from loguru import logger as l
data = ReadJson("./config.json")
l.info('config.json read')
def ReadConfig(name: str = "_") -> dict:
    l.info(f'config.json read for {name}')
    return data['plugin'][name]
