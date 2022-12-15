import base64
import json
import os

from arclet.alconna import Alconna
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Image, Plain, At
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.interrupt import FunctionWaiter
from graia.ariadne.util.validator import CertainMember, CertainFriend
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from arclet.alconna import Alconna
from arclet.alconna.graia import alcommand
from arclet.alconna import Alconna, Args, Arparma, MultiVar

from util.initializer import setting
from util.parseTool import parse_prefix
from util.spider import Session
from util.sqliteTool import (
    get_fursona,
    add_desc,
    add_fursona,
    get_name,
    get_random_fursona,
    session,
)

channel = Channel.current()

alcn = {
    "上传设定": Alconna("上传设定", parse_prefix("Fursona")),
    "设定": Alconna("设定", parse_prefix("Fursona")),
    "添加介绍{desc}": Alconna("添加介绍{desc}", parse_prefix("Fursona")),
    "随机设定": Alconna("随机设定", parse_prefix("Fursona")),
    "COMMIT": Alconna("COMMIT", parse_prefix("Fursona")),
    "设定{name}": Alconna("设定{name}", parse_prefix("Fursona")),
}
spider = Session("fursona")


def decode(s: str):
    return base64.standard_b64decode(s.encode()).decode()


def encode(s: str):
    return base64.standard_b64encode(s.encode()).decode()


def imgcmp(img: Image):
    return img.width > 4096 or img.height > 2160 or img.size / (1024**2) > 4


@alcommand(
    Alconna("上传设定", Args["img", MultiVar(Image)], parse_prefix("Fursona")),
    private=False,
)
async def setu(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    if not get_name(event.sender.id):
        await app.send_message(
            friend,
            MessageChain(Plain("请先设置圈名！")),
        )
        return
    else:
        img_list = []
        for img in result.main_args["img"]:
            if not os.path.exists(f"./db/{img.id}"):
                if imgcmp(img):
                    await app.send_message(friend, "警告:图片分辨率过大或图片体积过大,将会被自动压缩处理")
                await spider.download_file(img.url, f"./db/{img.id}")
            img_list.append(img.id)
        add_fursona(img_list, event.sender.id)


@alcommand(Alconna("上传设定", parse_prefix("Fursona")), private=False)
async def upload_img(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    await app.send_message(friend, Plain("请发送图片"))

    async def waiter(
        waiter_message: MessageChain,
    ):
        return waiter_message if waiter_message.has(Image) else "ERROR"

    if isinstance(friend, Group):
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
            if not os.path.exists(f"./db/{i.id}"):
                if imgcmp(i):
                    await app.send_message(friend, "警告:图片分辨率过大或图片体积过大,将会被自动压缩处理")
                await spider.download_file(i.url, f"./db/{i.id}")
            img_list.append(i.id)
        add_fursona(img_list, event.sender.id)


@alcommand(Alconna("上传设定", parse_prefix("Fursona")), private=True)
async def fursona(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    original_name = get_name(event.sender.id)
    if original_name:
        data = get_fursona(event.sender.id)
        if not data:
            await app.send_message(
                friend,
                MessageChain(Plain("你还没有上传设定")),
            )
            return
        await app.send_message(friend, raw_fursona_to_chain(data, original_name))
    else:
        await app.send_message(
            friend,
            MessageChain(Plain("请先设置圈名！")),
        )
        return


@alcommand(Alconna("添加介绍{desc}", parse_prefix("Fursona")), private=False)
async def add_fursona_desc(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    if get_name(event.sender.id) is not None:
        add_desc(result.header["desc"], event.sender.id)
    else:
        await app.send_message(
            friend,
            MessageChain(Plain("请先设置圈名！")),
        )
        return


@alcommand(Alconna("随机设定", parse_prefix("Fursona")), private=False)
async def random_fursona(app: Ariadne, friend: Friend | Group):
    data = get_random_fursona()
    if not data:
        await app.send_message(friend, MessageChain(Plain("设定库里还没有设定哦！")))
    else:
        await app.send_message(friend, raw_fursona_to_chain(data[0]))


def raw_fursona_to_chain(data, name: str | None = None):
    qq, img_json, desc = data
    real_name = get_name(qq) if name is None else name
    if not real_name:
        real_name = f"{qq}"
    else:
        real_name = f"{real_name}({qq})"
    return MessageChain(
        [
            [Image(path=f"./db/{i}") for i in json.loads(img_json)]
            + [[] if desc is None else Plain(decode(desc))]
            + Plain(f"主人：🐾{real_name}🐾")
        ]
    )


@alcommand(Alconna("设定{name}", parse_prefix("Fursona")), private=False)
async def specified_fursona_by_name(
    app: Ariadne, friend: Friend | Group, result: Arparma
):
    fur_name = result.header["name"]
    fur_qq = get_fursona(fur_name)
    if not fur_qq:
        await app.send_message(friend, MessageChain(Plain("这只兽还没有上传设定哦")))
        return
    await app.send_message(friend, raw_fursona_to_chain(fur_qq, result.header["name"]))


@alcommand(Alconna("设定", Args["at", At], parse_prefix("Fursona")), private=True)
async def specified_fursona_by_at(
    app: Ariadne, friend: Friend | Group, result: Arparma
):
    fursona_data = get_fursona(result.main_args["at"][0].target)
    if not fursona_data:
        await app.send_message(friend, MessageChain(Plain("这只兽还没有上传设定哦")))
    else:
        await app.send_message(friend, raw_fursona_to_chain(fursona_data))


@alcommand(Alconna("COMMIT", parse_prefix("Fursona")), private=True)
async def commit(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    if event.sender.id in setting["admins"]:
        session.commit()
    if event.sender.id not in setting["admins"]:
        await app.send_message(friend, "你没有管理员权限")
        return
