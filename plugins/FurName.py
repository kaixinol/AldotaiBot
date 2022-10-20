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
)
from util.sqliteTool import sqlLink
from util.initializer import *
from util.parseTool import *
import sys
import os
sys.path.append('../')


channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType('FurName')))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    from arclet.alconna import Alconna
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    ret = Alconna("设置圈名{name}", headers=parsePrefix(
        'FurName')).parse(message[Plain])
    if ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain(addName(ret.header['name'], event.sender.id))),
        )
        return
    ret = Alconna("我是谁").parse(message[Plain])
    if ret.matched:
        name = getName(event.sender.id)
        if name == "[未设置圈名]":
            await app.send_message(
                friend,
                MessageChain(Plain(f"你是……咦，我不知道你是谁")),
            )
            return
        else:
            await app.send_message(
                friend,
                MessageChain(Plain(f"你是{name}!")),
            )
            return
    ret = Alconna("教我画画").parse(message[Plain])
    if ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain(f"{getName(event.sender.id)}教我画画！！")),
        )
        return


@l.catch
def addName(n: str, qq: int) -> str:
    x = sqlLink('./db/furryData.db', b64=True)
    x.CreateTable('name', {'qq': int, 'name': str})
    ret = x.SearchData('name', ['qq', 'name'], require=dict)
    a, b = SafeIndex(ret, 'name', n), SafeIndex(ret, 'qq', qq)
    l.debug(SafeIndex(ret, 'name', n) == SafeIndex(ret, 'qq', qq) != -1)
    l.debug(f'{a},{b}')
    l.debug(ret)
    if SafeIndex(ret, 'name', n) == SafeIndex(ret, 'qq', qq) != -1:
        return f'你的圈名已经是{n}了'
    elif ret != {} and n in ret['name'] and a != -1:
        sm = ret['qq'][ret['name'].index(n)]
        return f'警告！您的圈名与{n}({sm})重名'
    if 'qq' in ret and qq not in ret['qq']:
        x.InsertTable('name', {'qq': qq, 'name': n})
    else:
        x.UpdateTable('name', struct={'select': [
            'qq', qq], 'data': {'qq': qq, 'name': n}})
    x.link.commit()
    return f'你的圈名现在是{n}了'


def SafeIndex(l: dict, key: str, wt: Any) -> int:
    if key not in l:
        return -1
    if wt not in l[key]:
        return -1
    return l[key].index(wt)


@l.catch
def getName(qq: int) -> str:
    x = sqlLink('./db/furryData.db', b64=True)
    x.CreateTable('name', {'qq': int, 'name': str})
    ret = x.SearchData('name', {
        'select': 'name', 'data': {'qq': qq}})
    return x.ToPureList(ret)[0] if len(ret) == 1 else '[未设置圈名]'


if __name__ == '__main__':
    x = sqlLink('./db/furryData.db', b64=True)
    l.debug(addName('阿尔多泰', 114514))
    l.debug(x.SearchData('name', ['qq', 'name'], require=list))
    l.debug(addName('阿尔多泰', 114))
    l.debug(x.SearchData('name', ['qq', 'name'], require=dict))
    l.debug(addName('阿斯奇琳', 114))
    l.debug(x.SearchData('name', ['qq', 'name'], require=dict))
    l.debug(addName('测你的码', 114))
    l.debug(x.SearchData('name', ['qq', 'name'], require=dict))
    l.debug(getName(114))
    l.debug(getName(115))
