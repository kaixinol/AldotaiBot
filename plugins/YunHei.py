import datetime
import re

import aiohttp
import html2text
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    At,
    Forward,
    ForwardNode,
    Plain,
)
from graia.ariadne.message.parser.twilight import RegexMatch, Twilight
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.saya import decorate, dispatch, listen
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger
from graia.ariadne.util.saya import decorate, dispatch, listen
from graia.saya import Channel, Saya
from arclet.alconna.graia import Alc, Match, AlconnaProperty, AlconnaSchema
from arclet.alconna.graia import Match, alcommand, from_command, startswith, endswith
from arclet.alconna import Alconna, Args, Arparma, MultiVar

from util.interval import GroupInterval
from util.parseTool import *

saya = Saya.current()
channel = Channel.current()


@alcommand(Alconna("查云黑{qq}", parse_prefix("YunHei")), private=False)
async def single_find(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    await app.send_message(
        friend,
        MessageChain(await is_blacklisted(result.header["qq"])),
    )


@alcommand(Alconna("查云黑", Args["at", At], parse_prefix("YunHei")), private=False)
async def at_somebody(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    await app.send_message(
        friend,
        MessageChain(await is_blacklisted(result.main_args["at"][0].target)),
    )


async def is_blacklisted(qq: int):
    keywords = {"qq": qq}
    url = "https://yunhei.qimeng.fun/"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=keywords) as resp:
            r = await resp.text()
    txt = html2text.html2text(r)
    return txt[txt.find("请输入账号或群号查询:") + 13 : txt.find("[举报上黑]") - 3]


async def is_member_blacklisted(qq: list):
    logger.debug(f"共{len(qq)}条数据")
    if len(qq) <= 200:
        keywords = {"qq": "\n".join([str(i) for i in qq])}
        url = "https://yunhei.qimeng.fun/Piliang.php"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=keywords) as resp:
                r = await resp.text()
        txt = html2text.html2text(r)
        return (
            re.sub(
                r"√\d{3,15}(未记录)?",
                "",
                txt[
                    txt.find("---------查询结果---------")
                    + 22 : txt.find("------------------------------")
                    - 2
                ],
            )
            .strip()
            .replace("×", "⚠️ ")
        )
    data = ""
    qq_list = chunk(qq, 200)
    for i in qq_list:
        keywords = {"qq": "\n".join([str(j) for j in i])}
        url = "https://yunhei.qimeng.fun/Piliang.php"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=keywords) as resp:
                r = await resp.text()
        txt = html2text.html2text(r)
        data += (
            re.sub(
                r"√\d{3,15}(未记录)?",
                "",
                txt[
                    txt.find("---------查询结果---------")
                    + 22 : txt.find("------------------------------")
                    - 2
                ],
            )
            .strip()
            .replace("×", "⚠️ ")
        )
        data += "\n"
    return data.replace("\n\n", "\n")


def chunk(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# @alcommand(Alconna("查群云黑", parse_prefix("YunHei")), private=False)
# @decorate(GroupInterval.require(60 * 20, 3, send_alert=True))
async def find_in_group(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    qq_member = await app.get_member_list(event.sender.group)
    if len(qq_member) > 200:
        await app.send_message(
            friend,
            MessageChain(f"数据较多……需要等待{2 * len(qq_member) / 200}秒"),
        )
    data = await is_member_blacklisted([i.id for i in qq_member])
    if not data:
        data = "无上云黑人员"
    if data.count("\n") > 5 or len(data) > 128:
        await app.send_message(
            friend,
            Forward(
                [
                    ForwardNode(
                        event.sender,
                        datetime.datetime(2022, 1, 14, 5, 14, 1),
                        MessageChain(data),
                        "阿尔多泰Aldotai",
                    )
                ]
            ),
        )
    else:
        await app.send_message(
            friend,
            MessageChain(data),
        )


# print(is_member_blacklisted([35464, 634132164, 643161, 16541365, 2352449583]))
