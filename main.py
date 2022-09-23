import pkgutil
from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.ariadne.event.message import GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group
from graia.saya import Saya
from plugins import jsonTool

saya = create(Saya)
configJson = jsonTool.ReadJson('config.json')
print([ii for ii in list(configJson['plugin'].keys())[:-1]
       if not configJson['plugin'][ii]['disabled']])
import sys
sys.path.append('plugins')

with saya.module_context():
    saya.require(f"plugins.resmonitor")
    saya.require(f"plugins.resmonitor")
    saya.require(f"plugins.OnlineCompile")

print()
app = Ariadne(
    config(
        verify_key="ServiceVerifyKey",  # 填入 VerifyKey
        account=2192808879,  # 你的机器人的 qq 号
    ),
)


app.launch_blocking()
