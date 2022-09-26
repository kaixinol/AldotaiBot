import sys
import os
sys.path.append('../')
from util.parseTool import *
from util.initializer import *
from util.sqliteTool import *

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
)
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel
from graia.ariadne.model import Group, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.app import Ariadne
from pyspectator.computer import Computer
from time import sleep
from pyspectator.convert import UnitByte
from collections.abc import MutableMapping
from graia.saya import Saya, Channel
from graia.saya.event import SayaModuleInstalled


channel = Channel.current()

async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")

@channel.use(ListenerSchema(listening_events=parseMsgType(ReadConfig('FurName'))))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    from arclet.alconna import Alconna
    message = event.message_chain
    ret=Alconna("设置圈名{name}", headers=parsePrefix(ReadConfig('FurName'))).parse(message[Plain])
    if ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain(addName(ret.header['name'],event.sender.id))),
        ) 
        return
    ret=Alconna("我是傻逼").parse(message[Plain])
    if ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain(f"你好!!我也是傻逼！！")),
        ) 
        return
    ret=Alconna("我是{name}").parse(message[Plain])
    if ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain(f"你好!!{ret.header['name']}")),
        ) 
        return
    ret=Alconna("教我画画").parse(message[Plain])
    if ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain(f"{getName(event.sender.id)}教我画画！！")),
        ) 
        return
    if HowTo(message.display)!=0:
        await app.send_message(
            friend,
            MessageChain(Plain('发送\n！设置圈名{你的圈名}\n不需要带空格')),
        )




from typing import Any
from loguru import logger as l
import re


@l.catch
def addName(n: str, qq: int) -> str:
    Connect('furryData.db')
    CreateTable('furryData.db', 'name', {'qq': 'int', 'name': 'str'})
    ret = SearchData('furryData.db', 'name', ['qq', 'name'])
    a, b = SafeIndex(ret, 'name', n), SafeIndex(ret, 'qq', qq)
    l.debug(SafeIndex(ret, 'name', n) == SafeIndex(ret, 'qq', qq) != -1)
    l.debug(f'{a},{b}')
    if SafeIndex(ret, 'name', n) == SafeIndex(ret, 'qq', qq) != -1:
        return f'你的圈名已经是{n}了'
    elif ret != {} and n in ret['name'] and a != -1:
        sm = ret['qq'][ret['name'].index(n)]
        return f'警告！您的圈名与{n}({sm})重名'
    if 'qq' in ret and qq not in ret['qq']:
        InsertTable('furryData.db', 'name', {'qq': qq, 'name': Encode(n)})
    else:
        UpdateTable('furryData.db', 'name', struct={'select': [
            'qq', qq], 'data': {'qq': qq, 'name': Encode(n)}})
    Commit('furryData.db')
    return f'你的圈名现在是{n}了'


def SafeIndex(l: dict, key: str, wt: Any) -> int:
    if key not in l:
        return -1
    if wt not in l[key]:
        return -1
    return l[key].index(wt)


@l.catch
def getName(qq: int) -> str:
    Connect('furryData.db')
    CreateTable('furryData.db', 'name', {'qq': 'int', 'name': 'str'})
    ret = SearchData('furryData.db', 'name', {
                     'select': 'name', 'data': {'qq': qq}})
    return ret[0] if len(ret) == 1 else '[未设置圈名]'


def HowTo(s: str):
    ret = re.search(r"(设置|圈名)(.{0,3})(设置|圈名)", s)
    return ret.span()[0]+ret.span()[1] if ret != None else 0


if __name__ == '__main__':
    l.debug(addName('阿尔多泰', 114514))
    l.debug(SearchData('furryData.db', 'name', ['qq', 'name']))
    l.debug(addName('阿尔多泰', 114))
    l.debug(SearchData('furryData.db', 'name', ['qq', 'name']))
    l.debug(addName('阿斯奇琳', 114))
    l.debug(SearchData('furryData.db', 'name', ['qq', 'name']))
    l.debug(addName('测你的码', 114))
    l.debug(SearchData('furryData.db', 'name', ['qq', 'name']))
    l.debug(getName(114))
    l.debug(getName(115))
    l.debug(HowTo('圈名是什么'))
    l.debug(HowTo('怎么设置圈名'))
