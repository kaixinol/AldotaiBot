import os
import sys
from typing import Any

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
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger as l

from util.initializer import *
from util.parseTool import *
from util.sqliteTool import sqlLink

sys.path.append("../")
x = sqlLink("./db/furryData.db", b64=True)
x.CreateTable("name", {"qq": int, "name": str})

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=parseMsgType("FurName")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    from arclet.alconna import Alconna

    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    ret = Alconna("设置圈名{name}", headers=parsePrefix("FurName")).parse(message[Plain])
    if ret.matched:
        if len(ret.header["name"])<12:
            await app.send_message(
            friend,
            MessageChain(Plain(addName(ret.header["name"], event.sender.id))),
        )
            return
        else:
            await app.send_message(
            friend,
            MessageChain(Plain('你的名字太长了，阿尔多泰记不住！')))
        
    ret = Alconna("我是谁").parse(message[Plain])
    if ret.matched:
        name = getName(event.sender.id)
        if name == "[未设置圈名]":
            await app.send_message(friend, MessageChain(Plain("你是……咦，我不知道你是谁")))
        else:
            await app.send_message(
                friend,
                MessageChain(Plain(f"你是{name}!")),
            )

        return


def addName(n: str, qq: int) -> str:
    ret = x.SearchData("name", ["qq", "name"])
    retDict = x.parseDataToDict(ret, ["qq", "name"])
    for i in ret:
        if i == [qq, n]:
            return f"你的圈名已经是{n}了"
        if (
            i[0] == qq
            and SafeIndex(retDict, "qq", qq) == SafeIndex(retDict, "name", n) != -1
        ):
            x.UpdateTable("name", {"select": ["qq", qq], "data": {"qq": qq, "name": n}})
            return f"你的圈名现在是{n}了"
        if i[1] == n and SafeIndex(retDict, "qq", qq) != SafeIndex(retDict, "name", n):
            same_name = retDict["qq"][retDict["name"].index(n)]
            return f"你的圈名与{same_name}重名"
    x.InsertTable("name", {"qq": qq, "name": n})
    return f"你的圈名现在是{n}了"


def SafeIndex(l: dict, key: str, wt) -> int:
    if key not in l:
        return -1
    return -1 if wt not in l[key] else l[key].index(wt)


def getName(qq: int) -> str:
    ret = x.SearchData("name", {"select": "name", "data": {"qq": qq}})
    return x.ToPureList(ret)[0] if len(ret) == 1 else "[未设置圈名]"


if __name__ == "__main__":
    x = sqlLink("./db/furryData.db", b64=True)
    l.debug(addName("阿尔多泰", 114514))
    l.debug(x.SearchData("name", ["qq", "name"], require=list))
    l.debug(addName("阿尔多泰", 114))
    l.debug(x.SearchData("name", ["qq", "name"], require=dict))
    l.debug(addName("阿斯奇琳", 114))
    l.debug(x.SearchData("name", ["qq", "name"], require=dict))
    l.debug(addName("测你的码", 114))
    l.debug(x.SearchData("name", ["qq", "name"], require=dict))
    l.debug(getName(114))
    l.debug(getName(115))
