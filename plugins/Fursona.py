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
from util.sqliteTool import *
import re
import sys
from loguru import logger as l
from plugins.FurName import getName
import os
import json
import wget

sys.path.append('../')


channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType(ReadConfig('Fursona'))))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    from arclet.alconna import Alconna
    message = event.message_chain
    ret = Alconna("上传设定", headers=parsePrefix(
        ReadConfig('Fursona'))).parse(message[Plain])
    imgList = []
    if ret.matched:
        if getName(event.sender.id) != "[未设置圈名]":
            for img in message.get(Image):
                if img.width > 2048 or img.height > 1080 or img.size/(1024*1024) > 3:
                    await app.send_message(
                        friend,
                        MessageChain(Plain("警告:图片分辨率过大或图片体积过大")),
                    )
                    return
                else:
                    wget.download(img.url, './db/{}'.format(img.id),bar=None)
                    imgList.append(img.id)
                    l.debug('./db/{}'.format(img.id))
            Connect('./db/furryData.db')
            CreateTable('./db/furryData.db', 'fursona',
                        {'qq': 'int', 'imgJson': 'str'})
            # TODO :img id去重
            UpdateTable('./db/furryData.db', 'fursona', struct={'select': [
                'qq', event.sender.id], 'data': {'qq': event.sender.id, 'imgJson': json.dumps(imgList)}})
            l.debug(SearchData('./db/furryData.db', "fursona", {
                'select': 'imgJson', 'data': {'qq':  event.sender.id}}))
        else:
            await app.send_message(
                friend,
                MessageChain(Plain("请先设置圈名！")),
            )
            return
