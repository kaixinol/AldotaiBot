import time

from arclet.alconna.graia import alcommand
from graia.ariadne.app import Ariadne
from arclet.alconna import Alconna, Arparma
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    Image,
    Plain,
)
from graia.ariadne.model import Group
from graia.saya import Channel, Saya

from util.parseTool import *
from util.spider import Session

saya = Saya.current()
channel = Channel.current()
spider = Session("EverydayFurry")


@alcommand(Alconna("每日一兽{name}", parse_prefix("EverydayFurry")), private=False)
async def today_furry(app: Ariadne, group: Group, result: Arparma):
    try:
        msg = await get_furry_img(result.header["name"])
        if msg is not None:
            await app.send_message(group, await get_chain(msg))
        else:
            await app.send_message(
                group, MessageChain(Plain(f"{result.header['name']}无兽兽推送捏"))
            )
    except Exception as e:
        await app.send_message(group, str(e))


@alcommand(Alconna("每日一兽", parse_prefix("EverydayFurry")), private=False)
async def today_furry(app: Ariadne, group: Group):
    msg = await get_furry_img()
    try:
        if msg is not None:
            await app.send_message(group, await get_chain(msg))
        else:
            await app.send_message(group, MessageChain(Plain(f"今日无兽兽推送捏")))
    except Exception as e:
        await app.send_message(group, str(e))


async def get_chain(msg: dict):
    return MessageChain(
        Image(**await spider.get_image(msg["pic"])),
        Plain(
            f"""
    来源：{msg["author"]}
    简介：{msg["desc"]}
    原文链接：{msg["org"]}
    详情：{msg['date']}
    """
        ),
    )


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
