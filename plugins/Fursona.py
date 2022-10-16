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
from util.sqliteTool import sqlLink
import re
import sys
from loguru import logger as l
from plugins.FurName import getName
import os
import json
import wget
from arclet.alconna import Alconna

sys.path.append('../')


channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType(ReadConfig('Fursona'))))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    ret = Alconna("上传设定", headers=parsePrefix(
        ReadConfig('Fursona'))).parse(message[Plain])
    if ret.matched:
        imgList = []
        if getName(event.sender.id) != "[未设置圈名]":
            for img in message.get(Image):
                if img.width > 2048 or img.height > 1080 or img.size/(1024*1024) > 3:
                    await app.send_message(
                        friend,
                        MessageChain(Plain("警告:图片分辨率过大或图片体积过大")),
                    )
                    return
                else:
                    if not os.path.exists('./db/{}'.format(img.id)):
                        wget.download(
                            img.url, './db/{}'.format(img.id), bar=None)
                    imgList.append(img.id)
                    l.debug('./db/{}'.format(img.id))
            x = sqlLink('./db/furryData.db')
            x.CreateTable('fursona',
                          {'qq': int, 'imgJson': str})
            x.UpdateTable('fursona', struct={'select': [
                'qq', event.sender.id], 'data': {'qq': event.sender.id, 'imgJson': json.dumps(imgList)}})
            l.debug('done')
            l.debug(x.SearchData("fursona", {
                'select': 'imgJson', 'data': {'qq':  event.sender.id}}))
            x.path.commit()
        else:
            await app.send_message(
                friend,
                MessageChain(Plain("请先设置圈名！")),
            )
            return


@channel.use(ListenerSchema(listening_events=parseMsgType(ReadConfig('Fursona'))))
async def fursona(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    ret = Alconna("设定", headers=parsePrefix(
        ReadConfig('Fursona'))).parse(message[Plain])
    if ret.matched and getName(event.sender.id) != "[未设置圈名]":
        x=sqlLink('./db/furryData.db')
        data = x.SearchData('./db/furryData.db', "fursona", {
            'select': 'imgJson', 'data': {'qq':  event.sender.id}})
        if data == []:
            await app.send_message(
                friend,
                MessageChain(Plain("你还没有上传设定")),
            )
            return
        rzt = json.loads(data[0])
        await app.send_message(
            friend,
            MessageChain([Image(path='./db/'+i) for i in rzt]),
        )

    elif ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain("请先设置圈名！")),
        )
        return
