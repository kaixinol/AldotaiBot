import asyncio
from email.policy import default
import random
import re
import base64
import aiohttp
from graia.saya.event import SayaModuleInstalled
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.mirai import MemberJoinEvent
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Friend
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.element import (
    Image,
    Plain,
    At,
    Quote,
    AtAll,
    Face,
    Poke,
    Forward,
    App,
    Json,
    Xml,
    MarketFace,
)
from util.initializer import *
from util.parseTool import *
import sys
sys.path.append('../')


saya = Saya.current()
channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType('FurName')))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    from arclet.alconna import Alconna
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    ret = Alconna("来只兽", headers=parsePrefix(
        'e621')).parse(message[Plain])
    config = ReadConfig('e621')
    if ret.matched:
        ret = await GetRandomFurryImg(config['default'][random.randint(0, len(config['default']))])
        await app.send_message(
            friend,
            MessageChain([Image(url=ret['url']), Plain(
                f'\nsources:{ret["sources"]}\nid:{ret["id"]}')]),
        )
    ret = Alconna("来只兽{name}", headers=parsePrefix(
        'e621')).parse(message[Plain])
    if ret.matched:
        ret = await GetRandomFurryImg(ret.header['name'])
        await app.send_message(
            friend,
            MessageChain([Image(url=ret['url']), Plain(
                f'\nsources:{ret["sources"]}\nid:{ret["id"]}')]),
        )

async def GetFurryJson(Tag: str) -> dict:
    config = ReadConfig('e621')
    if re.compile("[\u4e00-\u9fa5]").search(Tag):
        return None
    base64string = base64.b64encode(
        bytes("{}:{}" .format(config["username"], config["secret"]), "ascii")
    )
    url = f"https://e621.net/posts.json?tags=rating:s+{Tag}&limit=50"
    headers = {"User-Agent": "AldotaiBot/1.0 krawini",
               "Authorization": "Basic {}".format(base64string.decode("utf-8"))}
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
            "url": r"https://s1.ax1x.com/2022/07/23/jXR9D1.png",
            "sources": "None",
            "id": 114514,
        }
print(asyncio.run(GetRandomFurryImg('dog+cat')))
