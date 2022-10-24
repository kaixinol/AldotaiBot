import os
import sys

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
from loguru import logger as l

import util.jsonTool as js

l.add(
    os.getcwd() + "/log/{time: YYYY-MM-DD}.log",
    rotation="00:00",
    level="INFO",
    encoding="utf-8",
    filter=lambda rec: "graia" not in rec["name"] and "launart" not in rec["name"],
)

saya = create(Saya)
configJson = js.ReadJson("config.json5")

l.debug(
    str(
        [
            ii
            for ii in list(configJson["plugin"].keys())[:-1]
            if "disabled" not in configJson["plugin"][ii]
            or not configJson["plugin"][ii]["disabled"]
        ]
    )
)

sys.path.append("plugins")

with saya.module_context():
    for i in [
        ii
        for ii in list(configJson["plugin"].keys())[:-1]
        if "disabled" not in configJson["plugin"][ii]
        or not configJson["plugin"][ii]["disabled"]
    ]:
        saya.require(f"plugins.{i}")

app = Ariadne(
    config(
        3056337852,  # 你的机器人的 qq 号
        "ServiceVerifyKey",  # 填入 VerifyKey
        HttpClientConfig("http://127.0.0.1:8088/"),
        WebsocketClientConfig("http://127.0.0.1:8087"),
    ),
)


app.launch_blocking()
