import sys
import time

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

from util.parseTool import *
from util.spider import Session


saya = Saya.current()
channel = Channel.current()
alcn = {
    "每日一兽": Alconna("每日一兽", parse_prefix("EverydayFurry")),
    "每日一兽{name}": Alconna("每日一兽{name}", parse_prefix("EverydayFurry")),
}
spider = Session("EverydayFurry")


@channel.use(ListenerSchema(listening_events=parse_msg_type("EverydayFurry")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if not message[Plain]:
        return
    ret = alcn["每日一兽"].parse(message[Plain])
    ret2 = alcn["每日一兽{name}"].parse(message[Plain])
    if not ret.matched and not ret2.matched:
        return
    msg = None
    if ret.matched:
        msg = await get_furry_img()
    if ret2.matched:
        msg = await get_furry_img(ret2.header["name"])
    try:
        if msg is not None:
            await app.send_message(
                friend,
                MessageChain(
                    Image(**await spider.get_image(msg["pic"])),
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
    r = await spider.get_json(f"https://bot.hifurry.cn/everyfurry?date={d}")
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
