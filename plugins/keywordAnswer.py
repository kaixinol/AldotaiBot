import os
import re
import sys

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    App,
    At,
    AtAll,
    Face,
    Forward,
    Image,
    Json,
    MarketFace,
    Plain,
    Poke,
    Quote,
    Xml,
)
from graia.ariadne.model import Friend, Group
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.event import SayaModuleInstalled
from loguru import logger as l

from plugins.FurName import getName
from util.initializer import *
from util.parseTool import parseMsgType, parsePrefix

sys.path.append("../")


channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType("keywordAnswer")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    from arclet.alconna import Alconna

    message = event.message_chain
    if len(message[Plain]) == 0 or ignore(
        message.display, ReadConfig("keywordAnswer")["ignore"]
    ):
        return
    data = ReadConfig("keywordAnswer")
    ret = ""

    for i in data["react"]:
        if i[0].startswith("Alconna:") and not ignore(
            message.display, ReadConfig("keywordAnswer")["alconna"]
        ):
            t = i[0].replace("Alconna:", "")
            Ret = Alconna(t).parse(message.display)
            if Ret.matched:
                await app.send_message(
                    friend,
                    MessageChain(Plain(replaceMsg(i[1], Ret.header))),
                )
        if not i[0].startswith("Alconna:") and eval(i[0], globals(), locals()):
            msg = eval(i[1], globals(), locals())
            await app.send_message(
                friend,
                MessageChain(Plain(msg)),
            )


def ignore(s: str, db: list):
    for i in db:
        if (
            "Reg:" in i
            and re.search(i.replace("Reg:", ""), s).span() != (0, 0)
            or s.find(i) == 0
        ):
            l.debug(
                "Reg:{}\t{},Find:{}".format(
                    "Reg:" in i
                    and re.search(i.replace("Reg:", ""), s).span() != (0, 0),
                    i.replace("Reg:", ""),
                    s.find(i),
                )
            )
            return True
    return False


def replaceMsg(s: str, d: dict):
    for i in d:
        s = s.replace("{" + i + "}", d[i])
    return s
