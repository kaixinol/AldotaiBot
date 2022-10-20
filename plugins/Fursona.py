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
from arclet.alconna import Alconna, Option, Subcommand, Args
import base64
sys.path.append('../')


channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=parseMsgType('Fursona')))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    ret = Alconna("上传设定", headers=parsePrefix(
        'Fursona')).parse(message[Plain])
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
                          {'qq': int, 'imgJson': str, 'desc': str})
            x.UpdateTable('fursona', struct={'select': [
                'qq', event.sender.id], 'data': {'qq': event.sender.id, 'imgJson': json.dumps(imgList)}})
            l.debug(x.SearchData("fursona", {
                'select': 'imgJson', 'data': {'qq':  event.sender.id}}))
        else:
            await app.send_message(
                friend,
                MessageChain(Plain("请先设置圈名！")),
            )
            return


@channel.use(ListenerSchema(listening_events=parseMsgType('Fursona')))
async def fursona(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    ret = Alconna("设定", headers=parsePrefix(
        'Fursona')).parse(message[Plain])
    if ret.matched and getName(event.sender.id) != "[未设置圈名]":
        x = sqlLink('./db/furryData.db')
        data = x.ToPureList(x.SearchData("fursona", {
            'select': 'imgJson', 'data': {'qq':  event.sender.id}}))
        desc = x.ToPureList(x.SearchData("fursona", {
            'select': 'desc', 'data': {'qq':  event.sender.id}}))[0]
        if data == []:
            await app.send_message(
                friend,
                MessageChain(Plain("你还没有上传设定")),
            )
            return
        rzt = json.loads(data[0])
        await app.send_message(
            friend,
            MessageChain([Image(path='./db/'+i) for i in rzt] +
                         [Plain('') if desc==None else Plain(decode(desc)+'\n')]+[Plain(f'主人：🐾{getName(event.sender.id)}({event.sender.id})🐾')]),
        )

    elif ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain("请先设置圈名！")),
        )
        return


@channel.use(ListenerSchema(listening_events=parseMsgType('FurName')))
async def addDesc(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    ret = Alconna("添加介绍{desc}", headers=parsePrefix(
        'Fursona')).parse(message[Plain])
    if ret.matched and getName(event.sender.id) != "[未设置圈名]":
        x = sqlLink('./db/furryData.db')
        x.Execute(f'UPDATE fursona SET desc = \'{encode(ret.header["desc"])}\' WHERE qq={event.sender.id};')
  
    elif ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain("请先设置圈名！")),
        )
        return
def decode(s: str):
        return base64.standard_b64decode(
            s.encode()).decode()
def encode(s: str):
        return base64.standard_b64encode(
            s.encode()).decode()
