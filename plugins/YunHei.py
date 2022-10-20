from arclet.alconna import Alconna
from itertools import islice
import requests
import html2text
import re
import datetime
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
from  graia.ariadne.util.cooldown import CoolDown
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
            MessageChain(IsBlacklisted(qq.header['qq'])),
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
            MessageChain(IsBlacklisted(message[At][0].target)),
        )



def IsBlacklisted(qq: int):
    keywords = {"qq": qq}
    url = "https://yunhei.qimeng.fun/"
    r = requests.post(url, data=keywords)
    txt = html2text.html2text(r.text)
    return txt[txt.find("请输入账号或群号查询:") + 13: txt.find("[举报上黑]") - 3]


async def IsMemberBlacklisted(qq: list):
    if len(qq)<=200:
        keywords = {"qq": '\n'.join([str(i) for i in qq])}
        url = "https://yunhei.qimeng.fun/Piliang.php"
        r = requests.post(url, data=keywords)
        txt = html2text.html2text(r.text)
        return re.sub(r'√\d{3,15}(未记录)?', '', txt[txt.find("---------查询结果---------")+22: txt.find("------------------------------")-2]).strip().replace('×', '⚠️ ')
    else:
        data=""
        qqList=chunk(qq,199)
        for i in qqList:

            keywords = {"qq": '\n'.join([str(i) for i in qqList])}
            #print('\n'.join([str(i) for i in qq]))
            url = "https://yunhei.qimeng.fun/Piliang.php"
            #print('working...')
            await asyncio.sleep(0.1)
            r = requests.post(url, data=keywords)
            txt = html2text.html2text(r.text)
           # l.info(txt[txt.find("---------查询结果---------")+22: txt.find("------------------------------")-2])
            data+=re.sub(r'√\d{3,15}(未记录)?', '', txt[txt.find("---------查询结果---------")+22: txt.find("------------------------------")-2]).strip().replace('×', '⚠️ ')
        return data
def chunk(it, size):
    it = iter(it)
    return iter(lambda: list(islice(it, size)), ())


#@channel.use(ListenerSchema(listening_events=parseMsgType('YunHei')))
@bcc.receiver(GroupMessage, dispatchers=[CoolDown(5)])
async def GroupFind(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    qq = Alconna("查群云黑", headers=parsePrefix(
        'YunHei')).parse(message.display)
    if not qq.matched:
        return
    data = await IsMemberBlacklisted([i.id for i in  await app.get_member_list(event.sender.group)])
    if len(data)==0:
        data='无上云黑人员'
    if data.count('\n') > 5 or len(data)>128:
        await app.send_message(
            friend,
            Forward([ForwardNode(event.sender, datetime.datetime(2022, 1, 14, 5, 14, 1), MessageChain(data), '阿尔多泰Aldotai')]))
    else:
        await app.send_message(
            friend,
            MessageChain(data),
        )


#print(IsMemberBlacklisted([35464, 634132164, 643161, 16541365, 2352449583]))
