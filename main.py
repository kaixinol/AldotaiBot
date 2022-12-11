import os
import sys

from creart import create
from graia.ariadne.app import Ariadne
from graia.ariadne.connection.config import (
    HttpClientConfig,
    WebsocketClientConfig,
    config,
)
from graia.saya import Saya
from loguru import logger as l

import util.jsonTool as JS

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
    os.getcwd() + "/log/{time:YYYY-MM-DD}/sql.log",
    rotation="00:00",
    level="INFO",
    encoding="utf-8",
    filter=lambda rec: rec["name"] == "util.sqliteTool",
)
l.add(
    f"{os.getcwd()}/log/groupEvent.log",
    rotation="00:00",
    level="INFO",
    encoding="utf-8",
    filter=lambda rec: rec["name"] == "plugins.Logger",
)


saya = create(Saya)
configJson = JS.read_json("config.json5")

enabled_plugins = [
    ii
    for ii in list(configJson["plugin"].keys())[:-1]
    if "disabled" not in configJson["plugin"][ii]
    or not configJson["plugin"][ii]["disabled"]
]
l.debug(f"共加载{len(enabled_plugins)}个插件。{enabled_plugins}")

with saya.module_context():
    for i in enabled_plugins:
        saya.require(f"plugins.{i}")

app = Ariadne(
    config(
        2634732881,  # 你的机器人的 qq 号
        "ServiceVerifyKey",  # 填入 VerifyKey
        HttpClientConfig("http://127.0.0.1:8088/"),
        WebsocketClientConfig("http://127.0.0.1:8087"),
    ),
)

app.launch_blocking()
