from jsonTool import *
from logTool import *
data = ReadJson("./config.json")
info('config.json read')
def ReadConfig(name: str = "_") -> dict:
    info(f'config.json read for {name}')
    return data['plugin'][name]
