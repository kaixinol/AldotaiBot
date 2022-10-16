import util.jsonTool as js
from loguru import logger as l
data = js.ReadJson("./config.json")
l.info('config.json read')
def ReadConfig(name: str = "_") -> dict:
    l.debug(f'config.json read for {name}')
    return data['plugin'][name] if name in data['plugin'] else data[name]
