from arclet.alconna import Alconna
import sys
import time

import aiohttp
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

sys.path.append("../")


saya = Saya.current()
channel = Channel.current()
alcn = {
    "每日一兽": Alconna("每日一兽", parsePrefix("EverydayFurry")),
    "每日一兽{name}": Alconna("每日一兽{name}", parsePrefix("EverydayFurry")),
}


@channel.use(ListenerSchema(listening_events=parseMsgType("EverydayFurry")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    ret = alcn["每日一兽"].parse(message[Plain])
    ret2 = alcn["每日一兽{name}"].parse(message[Plain])
    if not ret.matched and not ret2.matched:
        return
    if ret.matched:
        msg = await get_furry_img()
    if ret2.matched:
        msg = await get_furry_img(ret2.header["name"])
    try:
        if msg is not None:
            await app.send_message(
                friend,
                MessageChain(
                    Image(url=msg["pic"]),
                    Plain(
                        f"""
来源：{msg["author"]}
简介：{msg["desc"]}
原文链接：{msg["org"]}
详情：{msg['date']}
"""
                    ),
                ),
            )
        else:
            await app.send_message(friend, MessageChain(Plain("今日无兽兽推送捏")))
    except Exception as e:
        await app.send_message(friend, MessageChain(Plain(str(e))))


async def get_furry_img(d: str = "today"):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://bot.hifurry.cn/everyfurry?date={d}") as resp:
            r = await resp.json()
            return (
                {
                    "pic": r["PictureUrl"],
                    "author": r["AuthorName"],
                    "desc": r["WorkInformation"],
                    "org": r["SourceLink"],
                    "date": f'https://bot.hifurry.cn/everyfurry?date={time.strftime("%Y%m%d")}',
                }
                if r["StateCode"]
                else None
            )
