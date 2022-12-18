import os
from asyncio import new_event_loop

from arclet.alconna.graia import AlconnaBehaviour
from arclet.alconna.manager import command_manager
from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.broadcast import Broadcast
from graia.saya import Saya
from loguru import logger as l

from util.initializer import setting

l.add(
    os.getcwd() + "/log/{time:YYYY-MM-DD}/bot.log",
    rotation="00:00",
    level="INFO",
    encoding="utf-8",
    filter=lambda rec: "graia" not in rec["name"]
    and "launart" not in rec["name"]
    and rec["name"] not in ["util.sqliteTool", "plugins.Logger"],
)

l.add(
    os.getcwd() + "/log/{time:YYYY-MM-DD}/graia.log",
    rotation="00:00",
    level="INFO",
    encoding="utf-8",
    compression="xz",
    filter=lambda rec: "graia" in rec["name"] or "launart" in rec["name"],
)

l.add(
    f"{os.getcwd()}/log/groupEvent.log",
    rotation="00:00",
    level="INFO",
    encoding="utf-8",
    filter=lambda rec: rec["name"] == "plugins.Logger",
)
loop = new_event_loop()
bcc = Broadcast(loop=loop)
saya = create(Saya)
create(AlconnaBehaviour)
saya.install_behaviours(AlconnaBehaviour(bcc, manager=command_manager))
enabled_plugins = [
    ii
    for ii in list(setting["plugin"].keys())[:-1]
    if "disabled" not in setting["plugin"][ii] or not setting["plugin"][ii]["disabled"]
]
l.debug(f"共加载{len(enabled_plugins)}个插件。{enabled_plugins}")

with saya.module_context():
    for i in enabled_plugins:
        saya.require(f"plugins.{i}")

app = Ariadne(
    config(
        setting["qq"],  # 你的机器人的 qq 号
        setting["verifykey"],  # 填入 VerifyKey
        HttpClientConfig(setting["client"]["HttpClientConfig"]),
        WebsocketClientConfig(setting["client"]["WebsocketClientConfig"]),
    ),
)


app.launch_blocking()
