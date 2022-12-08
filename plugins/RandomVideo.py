import asyncio
import os
import sys
from random import randint

import aiohttp
from arclet.alconna import Alconna
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.element import (
    Image,
    Plain,
)
from graia.ariadne.model import Friend, Group
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger as l

from util.parseTool import *
from util.spider import Session

sys.path.append("../")
config_data = setting["plugin"]["RandomVideo"]
spider = Session()
spider.init("randomvideo")

channel = Channel.current()
data = asyncio.run(
    spider.get_json(
        f'https://api.bilibili.com/x/v3/fav/resource/list?media_id={config_data["fav_id"]}&ps=20'
    )
)["data"]["medias"]
l.info(f"缓存了{len(data)}条数据")
alcn = {"来个meme": Alconna("来个meme", parse_prefix("RandomVideo"))}


@channel.use(ListenerSchema(listening_events=parse_msg_type("RandomVideo")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain

    async def get_good_data():
        rt = (
            await spider.get_json(
                f'https://api.bilibili.com/x/web-interface/archive/related?bvid={data[randint(0, len(data) - 1)]["bvid"]}'
            )
        )["data"]
        return rt or await get_good_data()

    if alcn["来个meme"].parse(message[Plain]).matched:
        datat = await get_good_data()
        data2 = datat[randint(0, len(datat) - 1)]
        try:
            await app.send_message(
                friend,
                [
                    Plain(data2["title"] + "\n")
                    + Image(**await spider.get_image(data2["pic"] + "@400w.png"))
                    + Plain("https://www.bilibili.com/video/" + data2["bvid"])
                ],
            )
        except Exception as e:
            await app.send_message(
                friend,
                [
                    Image(url=f"file:///{os.getcwd()}/res/error.jpg")
                    + Plain(f"发生了错误，{str(e)}")
                ],
            )