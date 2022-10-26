import asyncio
import base64
import os
import random
import re
import sys

import aiohttp
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.event.mirai import MemberJoinEvent
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
from graia.ariadne.model import Friend, Group, Member, MemberPerm
from graia.ariadne.util.saya import decorate, listen
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.event import SayaModuleInstalled

from util.control import GroupPermission
from util.interval import GroupInterval
from util.initializer import *
from util.parseTool import *

sys.path.append("../")


saya = Saya.current()
channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@listen(GroupMessage)
@decorate(GroupPermission.require(), GroupInterval.require(20, 10, send_alert=True))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    from arclet.alconna import Alconna

    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    config = ReadConfig("e621")
    ret = Alconna("来只兽", headers=parsePrefix("e621")).parse(message[Plain])
    ret2 = Alconna("来只兽{name}", headers=parsePrefix("e621")).parse(message[Plain])
    if not ret.matched and not ret2.matched:
        return
    if ret.matched:
        ret = await GetRandomFurryImg(
            config["default"][random.randint(0, len(config["default"]) - 1)]
        )
    if ret2.matched:
        ret = await GetRandomFurryImg(ret2.header["name"].replace(",", "+"))

    config = ReadConfig("e621")
    await app.send_message(
        friend,
        MessageChain(
            [
                Image(url=ret["url"]),
                Plain(f'\nsources:{ret["sources"][-2:]}\nid:{ret["id"]}'),
            ]
        ),
    )


async def GetFurryJson(Tag: str, context: str = "Safe") -> dict:
    t = {"Safe": "s", "Questionable": "q", "Explicit": "e"}[context]
    config = ReadConfig("e621")
    if re.compile("[\u4e00-\u9fa5]").search(Tag):
        return None
    base64string = base64.b64encode(
        bytes(f'{config["username"]}:{config["secret"]}', "ascii")
    )

    url = f"https://e621.net/posts.json?tags=rating:{t}+{Tag}&limit=50"
    headers = {
        "User-Agent": "AldotaiBot/1.0 krawini",
        "Authorization": f'Basic {base64string.decode("utf-8")}',
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            r = await resp.json()
            return r


async def GetRandomFurryImg(Tag: str):
    try:
        buffer = (await GetFurryJson(Tag))["posts"]
        aBuffer = buffer[random.randint(0, len(buffer) - 1)]
        return {
            "url": aBuffer["sample"]["url"],
            "sources": aBuffer["sources"],
            "id": aBuffer["id"],
        }
    except:
        return {
            "url": rf"file:///{os.getcwd()}/res/error.jpg",
            "sources": ["发生了错误！可能由于网络错误或api配置不正确"],
            "id": 114514,
        }


# print(asyncio.run(GetRandomFurryImg("dog+cat")))
