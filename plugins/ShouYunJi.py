from tempfile import TemporaryFile
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
from util.interval import GroupInterval

from graia.ariadne.message.parser.twilight import RegexMatch, Twilight
from util.initializer import *
from util.parseTool import *
from graia.ariadne.util.saya import decorate, dispatch, listen
from graia.ariadne.util.validator import CertainMember, CertainFriend
from graia.ariadne.util.interrupt import FunctionWaiter
from urllib.parse import quote_plus
import io
from PIL import Image as Img
alcn = {
    "兽兽": Alconna("兽兽", headers=parsePrefix("ShouYunJi")),
    "兽兽{name}": Alconna("兽兽{name}", headers=parsePrefix("ShouYunJi")),
    "上传兽云祭{name}": Alconna("上传兽云祭{name}"),
}


@listen(GroupMessage)
@dispatch(Twilight(RegexMatch(f"^兽兽")))
@decorate(GroupInterval.require(10, 3, send_alert=True))
async def rd(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    if alcn["兽兽"].parse(message[Plain]).matched:
        data = await GetFurryJson("https://cloud.foxtail.cn/api/function/random")
        data2 = await GetFurryJson(
            f'https://cloud.foxtail.cn/api/function/pictures?picture={data["picture"]["id"]}&model=1'
        )
        await app.send_message(
            friend,
            MessageChain(
                [
                    Plain(f'名字:{data2["name"]}'),
                    Image(data_bytes=await get_byte_from_url(data2["url"])),
                    Plain(f'id:{data2["picture"]}'),
                ]
            ),quote=event.id
        )


@listen(GroupMessage)
@dispatch(Twilight(RegexMatch(f"^(兽兽).+")))
@decorate(GroupInterval.require(20, 3, send_alert=True))
async def rdfurry(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    ret = alcn["兽兽{name}"].parse(message[Plain])
    if ret.matched:
        try:
            data = (
                await GetFurryJson(
                    f'https://cloud.foxtail.cn/api/function/pulllist?name={ret.header["name"]}'
                )
            )["open"]
            datat = data[randint(0, len(data) - 1)]
            data2 = await GetFurryJson(
                f'https://cloud.foxtail.cn/api/function/pictures?picture={datat["id"]}&model=1'
            )
            await app.send_message(
                friend,
                MessageChain(
                    [
                        Plain(f'名字:{data2["name"]}'),
                        Image(data_bytes=await get_byte_from_url(data2["url"])),
                        Plain(f'id:{data2["picture"]}'),
                    ]
                ),quote=event.id,
            )
        except:
            await app.send_message(
                friend, MessageChain([Plain(f"可能没有此兽xvx")]), quote=event.id
            )


async def GetFurryJson(s: str) -> dict:
    async with aiohttp.ClientSession() as session:
        headers = {
            "User-Agent": "AldotaiBot/1.0 Askirin",
        }
        async with session.get(s, headers=headers) as resp:
            return await resp.json()


@listen(GroupMessage)
@dispatch(Twilight(RegexMatch(f"^(上传兽云祭).+")))
@decorate(GroupInterval.require(10, 3, send_alert=True))
async def upload_shouyunji(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    # await async_download(message.url,message.id)
    message = event.message_chain
    ret = alcn["上传兽云祭{name}"].parse(message[Plain]).header["name"]
    p = {}
    p["name"] = quote_plus(ret)
    # WAITER

    def waiter(
        waiter_message: MessageChain,
    ):
        return waiter_message[Image][0] if waiter_message.has(Image) else "ERROR"

    def waiter2(
        waiter_message: MessageChain,
    ):
        return waiter_message if waiter_message.display in ["0", "1", "2"] else "ERROR"

    await app.send_message(friend, Plain("请发送图片"))
    # INIT IMG
    result = await FunctionWaiter(
        waiter,
        [GroupMessage],
        decorators=[CertainMember(event.sender.id, event.sender.group)],
        block_propagation=True,
    ).wait(timeout=30, default="ERROR")
    if result == "ERROR":
        await app.send_message(friend, Plain("超时或类型不对，取消操作"))
    else:
        await async_download(result.url, result.id)
        p["file"] = open(result.id, mode="r+b")
    await app.send_message(friend, Plain("请发送类型数字\n0.设定 1.毛图  2.插画"))
    # INIT TYPE
    result2 = await FunctionWaiter(
        waiter2,
        [GroupMessage],
        decorators=[CertainMember(event.sender.id, event.sender.group)],
        block_propagation=True,
    ).wait(timeout=30, default="ERROR")
    if result2 == "ERROR":
        await app.send_message(friend, Plain("超时或类型不对，取消操作"))
    else:
        p["type"] = result2.display
    async with aiohttp.ClientSession() as session:
        url = "https://cloud.foxtail.cn/api/function/upload"
        s = await session.post(url, data=p)
        print(await s.json())
        os.remove(result.id)


async def async_download(url: str, save: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(resp.status)
            if resp.status == 200:
                with open(save, mode="wb") as f:
                    f.write(await resp.read())
                    f.close()


async def get_byte_from_url(url: str):
    async with aiohttp.ClientSession() as s:
        async with s.get(url) as r:
            if round(r.content_length / 1024**2) > 1:
                foo = Img.open(io.BytesIO(await r.read()))
                foo.thumbnail((1000, 1000))
                img_byte_arr = io.BytesIO()
                foo.save(img_byte_arr, format="PNG", optimize=True, quality=85)
                img_byte_arr = img_byte_arr.getvalue()
                return img_byte_arr
            else:
                return await r.read()
