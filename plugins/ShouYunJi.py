import os
from random import choice
from re import match
from urllib.parse import quote_plus

import aiohttp
from arclet.alconna import Alconna, Arparma
from arclet.alconna.graia import alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    Image,
    Plain,
)
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.interrupt import FunctionWaiter
from graia.ariadne.util.validator import CertainMember
from graiax.shortcut.saya import decorate

from util.interval import GroupInterval
from util.parseTool import *
from util.spider import Session

spider = Session("ShouYunJi")


@alcommand(Alconna("兽兽"), private=False)
@decorate(GroupInterval.require(20, 3, send_alert=True))
async def random_furry(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    data = await spider.get_json("https://cloud.foxtail.cn/api/function/random")
    data2 = await spider.get_json(
        f'https://cloud.foxtail.cn/api/function/pictures?picture={data["picture"]["id"]}&model=1'
    )
    await app.send_message(
        friend,
        MessageChain(
            [
                Plain(f'名字:{data2["name"]}'),
                Image(**await spider.get_image(data2["url"])),
                Plain(f'id:{data2["picture"]}'),
            ]
        ),
        quote=event.id,
    )


@alcommand(Alconna("兽兽{name}"), private=False)
@decorate(GroupInterval.require(20, 3, send_alert=True))
async def get_furry_by_name(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    try:
        data = (
            await spider.get_json(
                f'https://cloud.foxtail.cn/api/function/pulllist?name={result.header["name"]}'
            )
        )["open"]
        datat = choice(data)
        data2 = await spider.get_json(
            f'https://cloud.foxtail.cn/api/function/pictures?picture={datat["id"]}&model=1'
        )
        await app.send_message(
            friend,
            MessageChain(
                [
                    Plain(f'名字:{data2["name"]}'),
                    Image(**await spider.get_image(data2["url"]))
                    if data2["examine"] in [0, 1]
                    else Plain("\n" + data2["msg"]),
                    Plain(f'\nid:{data2["picture"]}'),
                ]
            ),
            quote=event.id,
        )
    except IndexError:
        await app.send_message(
            friend, MessageChain([Plain("可能没有此兽xvx")]), quote=event.id
        )


@alcommand(Alconna("id为{id}的兽"), private=False)
@decorate(GroupInterval.require(10, 3, send_alert=True))
async def get_furry_by_id(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    if match(r"\d+", result.header["id"]) is not None:
        model = "1"
    else:
        model = "0"
    try:
        data = await spider.get_json(
            f'https://cloud.foxtail.cn/api/function/pictures?picture={result.header["id"]}&model={model}'
        )
        await app.send_message(
            friend,
            MessageChain(
                [
                    Plain(f'名字:{data["name"]}'),
                    Image(**await spider.get_image(data["url"]))
                    if data["examine"] in [0, 1]
                    else Plain("\n" + data["msg"]),
                    Plain(f'\nid:{data["picture"]}'),
                ]
            ),
            quote=event.id,
        )
    except IndexError:
        await app.send_message(
            friend, MessageChain([Plain("可能没有此兽xvx")]), quote=event.id
        )


@alcommand(Alconna("上传兽云祭{name}"), private=False)
@decorate(GroupInterval.require(10, 3, send_alert=True))
async def upload_shouyunji(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    # await async_download(message.url,message.id)
    message = event.message_chain
    ret = result.header["name"]
    p = {"name": quote_plus(ret)}

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
        # await async_download(result.url, result.id)
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
        # print(await s.json())
        os.remove(result.id)
