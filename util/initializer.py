from loguru import logger as l

import util.jsonTool as js

data = js.ReadJson("./config.json5")
l.info("config.json read")
def SaveConfig():
    js.CreateJson('config.json5',data)

def ReadConfig(name: str = "_") -> dict | list:
    # l.debug(f'config.json read for {name}')
    return data["plugin"][name] if name in data["plugin"] else data[name]
