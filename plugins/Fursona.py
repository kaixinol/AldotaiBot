import base64
import json
import os
import sys

import aiohttp
from arclet.alconna import Alconna
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.interrupt import FunctionWaiter
from graia.ariadne.util.validator import CertainMember, CertainFriend
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

from plugins.FurName import get_name
from util.initializer import setting
from util.parseTool import parse_prefix, parse_msg_type
from util.sqliteTool import sqlLink
from util.spider import Session

sys.path.append("../")

channel = Channel.current()

x = sqlLink("./db/furryData.db")
x.CreateTable("fursona", {"qq": int, "imgJson": str, "desc": str})
alcn = {
    "上传设定": Alconna("上传设定", parse_prefix("Fursona")),
    "设定": Alconna("设定", parse_prefix("Fursona")),
    "添加介绍{desc}": Alconna("添加介绍{desc}", parse_prefix("Fursona")),
}
spider = Session("fursona")


def imgcmp(img: Image):
    return img.width > 4096 or img.height > 2160 or img.size / (1024**2) > 4


@channel.use(ListenerSchema(listening_events=parse_msg_type("Fursona")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = alcn["上传设定"].parse(message[Plain])
    if not message.has(Image):
        return
    if ret.matched:
        if get_name(event.sender.id) == "[未设置圈名]":
            await app.send_message(
                friend,
                MessageChain(Plain("请先设置圈名！")),
            )
            return
        else:
            img_list = []
            for img in message.get(Image):
                if imgcmp(img):
                    await app.send_message(
                        friend,
                        MessageChain(Plain("警告:图片分辨率过大或图片体积过大")),
                    )
                    return
                else:
                    if not os.path.exists(f"./db/{img.id}"):
                        await spider.download_file(img.url, f"./db/{img.id}")
                    img_list.append(img.id)
            x.UpdateTable(
                "fursona",
                struct={
                    "select": ["qq", event.sender.id],
                    "data": {"qq": event.sender.id, "imgJson": json.dumps(img_list)},
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
        img_list = []
        for i in result[Image]:
            if imgcmp(i):
                await app.send_message(
                    friend,
                    MessageChain(Plain("警告:图片分辨率过大或图片体积过大")),
                )
                return
            if not os.path.exists(f"./db/{i.id}"):
                await spider.download_file(i.url, f"./db/{i.id}")
            img_list.append(i.id)
        x.UpdateTable(
            "fursona",
            struct={
                "select": ["qq", event.sender.id],
                "data": {"qq": event.sender.id, "imgJson": json.dumps(img_list)},
            },
        )


@channel.use(ListenerSchema(listening_events=parse_msg_type("Fursona")))
async def fursona(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = alcn["设定"].parse(message[Plain])
    if ret.matched:
        if get_name(event.sender.id) != "[未设置圈名]":
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
                        + [
                            Plain(
                                f"主人：🐾{get_name(event.sender.id)}({event.sender.id})🐾"
                            )
                        ]
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
async def add_desc(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    ret = alcn["添加介绍{desc}"].parse(message[Plain])
    if ret.matched and get_name(event.sender.id) != "[未设置圈名]":
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
