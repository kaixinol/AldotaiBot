from jsonTool import *
from contextvars import *
did = False
global obj
obj = None
if not did:
    data = ReadJson("./config.json")
    did = True
    print('json read')
def ReadConfig(name: str = "_") -> dict:
    print('read from memory')
    return data['plugin'][name]
