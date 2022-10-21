from arclet.alconna import Alconna
from itertools import islice
import html2text
import re
import datetime
import aiohttp
import asyncio
from loguru import logger as l
from typing import Any
from graia.saya.event import SayaModuleInstalled
from graia.saya import Saya, Channel
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.model import Group, Friend
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.ariadne.message.element import (
    Image,
    Plain,
    At,
    Quote,
    AtAll,
    Face,
    Poke,
    Forward,
    App,
    Json,
    Xml,
    MarketFace,
    ForwardNode
)
from util.sqliteTool import sqlLink
from util.initializer import *
from util.parseTool import *
from graia.ariadne.util.cooldown import CoolDown
from graia.broadcast import Broadcast as bcc
import sys
import os
sys.path.append('../')


channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType('YunHei')))
async def Single(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    qq = Alconna("查云黑{qq}",  headers=parsePrefix(
        'YunHei')).parse(message[Plain])
    if not qq.matched:
        return
    await app.send_message(
        friend,
        MessageChain(await IsBlacklisted(qq.header['qq'])),
    )


@channel.use(ListenerSchema(listening_events=parseMsgType('YunHei')))
async def Atsb(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    qq = Alconna("查云黑", headers=parsePrefix(
        'YunHei')).parse(message[Plain])
    if not qq.matched:
        return
    await app.send_message(
        friend,
        MessageChain(await IsBlacklisted(message[At][0].target)),
    )


async def IsBlacklisted(qq: int):
    keywords = {"qq": qq}
    url = "https://yunhei.qimeng.fun/"
    async with aiohttp.ClientSession() as session:
        async with session.post(url,
                                data=keywords) as resp:
            r = await resp.text()
    txt = html2text.html2text(r)
    return txt[txt.find("请输入账号或群号查询:") + 13: txt.find("[举报上黑]") - 3]


async def IsMemberBlacklisted(qq: list):
    l.debug(f'共{len(qq)}条数据')
    if len(qq) <= 200:
        keywords = {"qq": '\n'.join([str(i) for i in qq])}
        url = "https://yunhei.qimeng.fun/Piliang.php"
        async with aiohttp.ClientSession() as session:
            async with session.post(url,
                                    data=keywords) as resp:
                r = await resp.text()
        txt = html2text.html2text(r)
        return re.sub(r'√\d{3,15}(未记录)?', '', txt[txt.find("---------查询结果---------")+22: txt.find("------------------------------")-2]).strip().replace('×', '⚠️ ')
    else:
        data = ""
        qqList = chunk(qq,200)
        for i in qqList:
            keywords = {"qq": '\n'.join([str(j) for j in i])}
            url = "https://yunhei.qimeng.fun/Piliang.php"
            async with aiohttp.ClientSession() as session:
                async with session.post(url,
                                    data=keywords) as resp:
                    r = await resp.text()
            txt = html2text.html2text(r)
            data+=re.sub(r'√\d{3,15}(未记录)?', '', txt[txt.find("---------查询结果---------")+22: txt.find("------------------------------")-2]).strip().replace('×', '⚠️ ')
            data+='\n'
        return data.replace('\n\n','\n')


def chunk(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@channel.use(ListenerSchema(
    listening_events=parseMsgType('YunHei'),
    inline_dispatchers=[CoolDown(60*60)],
))
async def GroupFind(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    qq = Alconna("查群云黑", headers=parsePrefix(
        'YunHei')).parse(message.display)
    if not qq.matched:
        return
    qqMember=await app.get_member_list(event.sender.group)
    if len(qqMember) > 200:
        await app.send_message(
            friend,
            MessageChain(f'数据较多……需要等待{2*len(qqMember)/200}秒'),
        )
    data = await IsMemberBlacklisted([i.id for i in qqMember])
    if len(data) == 0:
        data = '无上云黑人员'
    if data.count('\n') > 5 or len(data) > 128:
        await app.send_message(
            friend,
            Forward([ForwardNode(event.sender, datetime.datetime(2022, 1, 14, 5, 14, 1), MessageChain(data), '阿尔多泰Aldotai')]))
    else:
        await app.send_message(
            friend,
            MessageChain(data),
        )

async def apiIsBlackListed():
        pass
        keywords = {"qq": 1}
        url = "https://yunhei.qimeng.fun/Piliang.php"
        async with aiohttp.ClientSession() as session:
            async with session.post(url,
                                    data=keywords) as resp:
                r = await resp.json()
        txt = html2text.html2text(r)

# print(IsMemberBlacklisted([35464, 634132164, 643161, 16541365, 2352449583]))
