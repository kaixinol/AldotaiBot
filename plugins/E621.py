import base64
import os
import random
import re
from json.decoder import JSONDecodeError

from arclet.alconna import Alconna, Arparma
from arclet.alconna.graia import alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.model import Friend, Group
from graia.saya import Channel, Saya
from graiax.shortcut.saya import decorate

from util.initializer import setting
from util.interval import MemberInterval
from util.parseTool import parse_prefix
from util.spider import Session

saya = Saya.current()
channel = Channel.current()
config = setting["plugin"]["E621"]

base64string = base64.b64encode(
    bytes(f'{config["username"]}:{config["secret"]}', "ascii")
)
spider = Session(
    {
        "User-Agent": "AldotaiBot/1.0 krawini",
        "Authorization": f'Basic {base64string.decode("utf-8")}',
    },
    proxy=True,
)


@alcommand(Alconna("来只兽", parse_prefix("E621")), private=False)
@decorate(MemberInterval.require(20, 5, send_alert=True))
async def get_furry(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    ret = await get_random_furry_img(random.choice(config["default"]))
    await app.send_message(
        friend,
        MessageChain(
            [
                Image(**await spider.get_image(ret["url"])),
                Plain(f'\nsources:{ret["sources"][-2:]}\nid:{ret["id"]}'),
            ]
        ),
        quote=event.id,
    )


@alcommand(Alconna("来只兽{name}", parse_prefix("E621")), private=False)
@decorate(MemberInterval.require(20, 5, send_alert=True))
async def get_furry_by_name(
    app: Ariadne, group: Group, result: Arparma, event: MessageEvent
):
    ret = await get_random_furry_img(result.header["name"].replace(",", "+"))
    await app.send_message(
        group,
        MessageChain(
            [
                Image(**await spider.get_image(ret["url"])),
                Plain(f'\nsources:{ret["sources"][-2:]}\nid:{ret["id"]}'),
            ]
        ),
        quote=event.id,
    )


async def get_furry_json(tag: str, context: str = "Safe") -> dict | None:
    t = {"Safe": "s", "Questionable": "q", "Explicit": "e"}[context]
    if re.compile("[\u4e00-\u9fa5]").search(tag):
        return None
    url = f"https://e621.net/posts.json?tags=rating:{t}+{tag}&limit=50"
    return await spider.get_json(url)


async def get_random_furry_img(tag: str):
    try:
        buffer = (await get_furry_json(tag))["posts"]
        a_buffer = buffer[random.randint(0, len(buffer) - 1)]
        return {
            "url": a_buffer["sample"]["url"],
            "sources": a_buffer["sources"],
            "id": a_buffer["id"],
        }
    except JSONDecodeError:
        return {
            "url": rf"file:///{os.getcwd()}/res/error.jpg",
            "sources": ["e621暂时处于cf保护中"],
            "id": 114514,
        }
    except KeyError:
        return {
            "url": rf"file:///{os.getcwd()}/res/error.jpg",
            "sources": ["API key 不正确"],
            "id": 114514,
        }
