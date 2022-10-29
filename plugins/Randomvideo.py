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
from io import BytesIO
from PIL import Image as im
sys.path.append("../")


async def getdata(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            r = await resp.json()
            return r
async def getfile(f: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(f) as resp:
            r =await resp.read()
            return r
channel = Channel.current()
data = asyncio.run(getdata(
    f'https://api.bilibili.com/x/v3/fav/resource/list?media_id={ReadConfig("Randomvideo")["fav_id"]}&ps=20'))['data']['medias']
print(data)


@channel.use(ListenerSchema(listening_events=parseMsgType("Randomvideo")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if Alconna("来个meme", headers=parsePrefix("Randomvideo")).parse(message[Plain]).matched:
      try:
        datat = (await getdata(f'https://api.bilibili.com/x/web-interface/archive/related?bvid={data[randint(0,len(data)-1)]["bvid"]}'))['data']
        data2 = datat[randint(0, len(datat)-1)]
        await app.send_message(friend, [Plain(data2['title']+'\n')+Image(url=data2['pic']+'@400w.png')+Plain('https://www.bilibili.com/video/'+data2['bvid'])])
      except:
        await app.send_message(friend, [Image(url=f"file:///{os.getcwd()}/res/error.jpg")+Plain('发生了错误，可能是因为超时或者风控')])


