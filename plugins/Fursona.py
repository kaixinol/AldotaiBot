import base64
import json
import os
import sys

import aiohttp
from arclet.alconna import Alconna
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.interrupt import FunctionWaiter
from graia.ariadne.util.validator import CertainMember, CertainFriend
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from plugins.FurName import getName
from util.initializer import *
from util.parseTool import *
from util.sqliteTool import sqlLink

sys.path.append("../")


channel = Channel.current()


x = sqlLink("./db/furryData.db")
x.CreateTable("fursona", {"qq": int, "imgJson": str, "desc": str})
alcn = {
    "上传设定": Alconna("上传设定", parse_prefix("Fursona")),
    "设定": Alconna("设定", parse_prefix("Fursona")),
    "添加介绍{desc}": Alconna("添加介绍{desc}", parse_prefix("Fursona")),
}


def imgcmp(img: Image):
    return img.width > 2048 or img.height > 1080 or img.size / (1024 * 1024) > 3


async def async_download(url: str, save: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            print(resp.status)
            if resp.status == 200:
                with open(save, mode="wb") as f:
                    f.write(await resp.read())
                    f.close()


@channel.use(ListenerSchema(listening_events=parse_msg_type("Fursona")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = alcn["上传设定"].parse(message[Plain])
    if not message.has(Image):
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
                if imgcmp(img):
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


@channel.use(ListenerSchema(listening_events=parse_msg_type("Fursona")))
async def upload_img(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = alcn["上传设定"].parse(message[Plain])
    if not ret.matched:
        return
    if message.has(Image):
        return
    await app.send_message(friend, Plain("请发送图片"))

    async def waiter(
        waiter_message: MessageChain,
    ):
        return waiter_message if waiter_message.has(Image) else "ERROR"

    if type(friend) == Group:
        result = await FunctionWaiter(
            waiter,
            [GroupMessage],
            decorators=[CertainMember(event.sender.id, event.sender.group)],
            block_propagation=True,
        ).wait(timeout=30, default="ERROR")
    else:
        result = await FunctionWaiter(
            waiter,
            [FriendMessage],
            decorators=[CertainFriend(event.sender.id)],
            block_propagation=True,
        ).wait(timeout=30, default="ERROR")
    if result == "ERROR":
        await app.send_message(friend, Plain("超时或类型不对，取消操作"))
    else:
        imgList = []
        for i in result[Image]:
            if imgcmp(i):
                await app.send_message(
                    friend,
                    MessageChain(Plain("警告:图片分辨率过大或图片体积过大")),
                )
                return
            if not os.path.exists(f"./db/{i.id}"):
                await async_download(i.url, f"./db/{i.id}")
            imgList.append(i.id)
        x.UpdateTable(
            "fursona",
            struct={
                "select": ["qq", event.sender.id],
                "data": {"qq": event.sender.id, "imgJson": json.dumps(imgList)},
            },
        )


@channel.use(ListenerSchema(listening_events=parse_msg_type("Fursona")))
async def fursona(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = alcn["设定"].parse(message[Plain])
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


@channel.use(ListenerSchema(listening_events=parse_msg_type("FurName")))
async def addDesc(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = alcn["添加介绍{desc}"].parse(message[Plain])
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
