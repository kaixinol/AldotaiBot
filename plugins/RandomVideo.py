import asyncio
import os
from random import randint

from arclet.alconna import Alconna
from arclet.alconna.graia import alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.message.element import (
    Image,
    Plain,
)
from graia.ariadne.model import Friend, Group
from graia.saya import Channel
from loguru import logger

from util.parseTool import *
from util.spider import Session

config_data = setting["plugin"]["RandomVideo"]
spider = Session("randomvideo")

channel = Channel.current()
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
data = loop.run_until_complete(
    spider.get_json(
        f'https://api.bilibili.com/x/v3/fav/resource/list?media_id={config_data["fav_id"]}&ps=20'
    )
)["data"]["medias"]
logger.info(f"缓存了{len(data)}条数据")


@alcommand(Alconna("来个meme", parse_prefix("RandomVideo")), private=False)
async def setu(app: Ariadne, friend: Friend | Group):
    async def get_good_data():
        rt = (
            await spider.get_json(
                f'https://api.bilibili.com/x/web-interface/archive/related?bvid={data[randint(0, len(data) - 1)]["bvid"]}'
            )
        )["data"]
        return rt or await get_good_data()

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
