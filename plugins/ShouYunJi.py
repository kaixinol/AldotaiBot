import asyncio
from random import randint
import aiohttp
import sys
import os
from arclet.alconna import Alconna
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    Image,
    Plain,
)
from graia.ariadne.model import Friend, Group
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger as l

from util.initializer import *
from util.parseTool import *
from graia.ariadne.util.saya import decorate, dispatch, listen


@listen(GroupMessage)
async def rd(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    from arclet.alconna import Alconna
    if Alconna("兽兽", headers=parsePrefix("ShouYunJi")).parse(message[Plain]).matched:
        data = await GetFurryJson('https://cloud.foxtail.cn/api/function/random')
        data2 = (await  GetFurryJson(f'https://cloud.foxtail.cn/api/function/pictures?picture={data["picture"]["id"]}&model=1'))
        await app.send_message(
            friend,
            MessageChain([Plain(f'名字:{data2["name"]}'),Image(url=data2['url']),Plain(f'id:{data2["picture"]}')]),
        )


@listen(GroupMessage)
async def rdfurry(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    from arclet.alconna import Alconna
    ret=Alconna("兽兽{name}", headers=parsePrefix("ShouYunJi")).parse(message[Plain])
    if ret.matched:
        data = (await GetFurryJson(f'https://cloud.foxtail.cn/api/function/pulllist?name={ret.header["name"]}'))['open']
        datat=data[randint(0,len(data)-1)]
        data2 = (await  GetFurryJson(f'https://cloud.foxtail.cn/api/function/pictures?picture={datat["id"]}&model=1'))
        await app.send_message(
            friend,
            MessageChain([Plain(f'名字:{data2["name"]}'),Image(url=data2['url']),Plain(f'id:{data2["picture"]}')]),
        )
async def GetFurryJson(s:str) -> dict:
    async with aiohttp.ClientSession() as session:
        headers = {
        "User-Agent": "AldotaiBot/1.0 Askirin",}
        async with session.get(s, headers=headers) as resp:
            return await resp.json()
