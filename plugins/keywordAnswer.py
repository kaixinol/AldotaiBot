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
from util.initializer import *
from util.parseTool import *
import re
import sys
from loguru import logger as l
import os
sys.path.append('../')


channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType('keywordAnswer')))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    from arclet.alconna import Alconna
    message = event.message_chain
    if len(message[Plain]) == 0 or ignore(message.display,ReadConfig('keywordAnswer')['ignore']):
        return
    data = ReadConfig('keywordAnswer')
    for i in data['react']:
        OK = False
        if 'regex' not in i:
            ret = Alconna(i['keyword'], headers=parsePrefix(
                'keywordAnswer')).parse(message[Plain])
            if not ret.matched:
                continue
            if ret.matched and ret.header != True:
                await app.send_message(
                    friend,
                    MessageChain(Plain(replaceMsg(i['respond'], ret.header))),
                )
                return
            if ret.matched == ret.header == True:
                await app.send_message(
                    friend,
                    MessageChain(Plain(i['respond'])),
                )
                return
        else:
            if reg(message.display, i['regex']):
                await app.send_message(
                    friend,
                    MessageChain(Plain(i['respond'])),
                )
                return
            continue


def ignore(s: str, db: list):
    for i in db:
        if 'Reg:' in i and re.search(i.replace('Reg:', ''), s).span() != (0, 0) or s.find(i) == 0:
            l.debug('Reg:{}\t{},Find:{}'.format('Reg:' in i and re.search(i.replace('Reg:', ''), s).span() != (0, 0),i.replace('Reg:', ''),s.find(i)))
            return True
    return False
    


def replaceMsg(s: str, d: dict):
    for i in d.keys():
        s = s.replace('{'+i+'}', d[i])
    return s


def reg(s: str, reg: str):
    ret = re.search(reg, s)
    return True if ret != None else False
