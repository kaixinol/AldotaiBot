import base64
import json
import os
import re
import sys
import wget
from graia.ariadne.util.async_exec import io_bound, cpu_bound
from graia.ariadne.util.interrupt import FunctionWaiter
from arclet.alconna import Alconna
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, Source
from graia.ariadne.model import Friend, Group, Member
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger as l

from plugins.FurName import getName
from util.initializer import *
from util.parseTool import *
from util.sqliteTool import sqlLink

sys.path.append("../")


channel = Channel.current()


x = sqlLink("./db/furryData.db")
x.CreateTable("fursona", {"qq": int, "imgJson": str, "desc": str})


@channel.use(ListenerSchema(listening_events=parseMsgType("Fursona")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = Alconna("上传设定", headers=parsePrefix("Fursona")).parse(message[Plain])
    if not message.get(Image):
        return
    if ret.matched:
        if getName(event.sender.id) == "[未设置圈名]":
            await app.send_message(
                friend,
                MessageChain(Plain("请先设置圈名！")),
            )
            return
        else:
            imgList = []
            for img in message.get(Image):
                if (
                    img.width > 2048
                    or img.height > 1080
                    or img.size / (1024 * 1024) > 3
                ):
                    await app.send_message(
                        friend,
                        MessageChain(Plain("警告:图片分辨率过大或图片体积过大")),
                    )
                    return
                else:
                    if not os.path.exists(f"./db/{img.id}"):
                        await async_download(img.url, f"./db/{img.id}")
                    imgList.append(img.id)
                    l.debug(f"./db/{img.id}")
            x.UpdateTable(
                "fursona",
                struct={
                    "select": ["qq", event.sender.id],
                    "data": {"qq": event.sender.id, "imgJson": json.dumps(imgList)},
                },
            )


@channel.use(ListenerSchema(listening_events=parseMsgType("Fursona")))
async def upload_img(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = Alconna("上传设定", headers=parsePrefix("Fursona")).parse(message[Plain])
    if not ret.matched:
        return
    await app.send_message(friend, Plain("请发送图片"))

    async def waiter(
        event: GroupMessage,
        waiter_member: Member,
        waiter_group: Group,
        waiter_message: MessageChain,
    ):
        if waiter_member.id == event.sender.id and waiter_group.id == friend.id:
            return waiter_message

    try:
        result = await FunctionWaiter(
            waiter, [GroupMessage], block_propagation=True
        ).wait(timeout=30)
    except asyncio.exceptions.TimeoutError:
            await app.send_message(
                friend, MessageChain("超时，取消操作!"), quote=message[Source][0]
        )
            return
    if not result[Image]:
            await app.send_message(friend, Plain("非图片，取消操作"))
    else:
            imgList = []
            for i in result[Image]:
                if not os.path.exists(f"./db/{i.id}"):
                    await async_download(i.url, f"./db/{i.id}")
                imgList.append(i.id)
                print(imgList)
            x.UpdateTable(
                "fursona",
                struct={
                    "select": ["qq", event.sender.id],
                    "data": {"qq": event.sender.id, "imgJson": json.dumps(imgList)},
                },
            )



import asyncio


async def async_download(url: str, save: str):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, wget.download, url, save)


@channel.use(ListenerSchema(listening_events=parseMsgType("Fursona")))
async def fursona(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = Alconna("设定", headers=parsePrefix("Fursona")).parse(message[Plain])
    if ret.matched:
        if getName(event.sender.id) != "[未设置圈名]":
            data = x.ToPureList(
                x.SearchData(
                    "fursona", {"select": "imgJson", "data": {"qq": event.sender.id}}
                )
            )
            if not data:
                await app.send_message(
                    friend,
                    MessageChain(Plain("你还没有上传设定")),
                )
                return
            desc = x.ToPureList(
                x.SearchData(
                    "fursona", {"select": "desc", "data": {"qq": event.sender.id}}
                )
            )[0]
            rzt = json.loads(data[0])
            await app.send_message(
                friend,
                MessageChain(
                    (
                        [Image(path=f"./db/{i}") for i in rzt]
                        + [Plain("") if desc is None else Plain(decode(desc) + "\n")]
                        + [Plain(f"主人：🐾{getName(event.sender.id)}({event.sender.id})🐾")]
                    )
                ),
            )

        else:
            await app.send_message(
                friend,
                MessageChain(Plain("请先设置圈名！")),
            )
            return


@channel.use(ListenerSchema(listening_events=parseMsgType("FurName")))
async def addDesc(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = Alconna("添加介绍{desc}", headers=parsePrefix("Fursona")).parse(message[Plain])
    if ret.matched and getName(event.sender.id) != "[未设置圈名]":
        x.Execute(
            f'UPDATE fursona SET desc = \'{encode(ret.header["desc"])}\' WHERE qq={event.sender.id};'
        )

    elif ret.matched:
        await app.send_message(
            friend,
            MessageChain(Plain("请先设置圈名！")),
        )
        return


def decode(s: str):
    return base64.standard_b64decode(s.encode()).decode()


def encode(s: str):
    return base64.standard_b64encode(s.encode()).decode()
