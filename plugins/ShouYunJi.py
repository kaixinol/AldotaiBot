import io
from asyncio import get_event_loop
from random import choice
from re import match

from arclet.alconna import Alconna, Arparma
from arclet.alconna.graia import alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, GroupMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import (
    Image,
    Plain,
)
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.interrupt import FunctionWaiter
from graia.ariadne.util.validator import CertainMember
from graiax.shortcut.saya import decorate
from loguru import logger

from util.interval import GroupInterval
from util.parseTool import *
from util.spider import Session

spider = Session("ShouYunJi")
sdata = setting["plugin"]["ShouYunJi"]
loop = get_event_loop()
setting["plugin"]["ShouYunJi"]["cookie"] = loop.run_until_complete(
    spider.get_cookie(
        "https://cloud.foxtail.cn/api/account/login",
        kw={
            "account": sdata["account"],
            "password": sdata["password"],
            "model": "1",
            "token": sdata["token"],
        },
    )
)
assert (
    loop.run_until_complete(
        spider.get_json(
            "https://cloud.foxtail.cn/api/account/state",
            setting["plugin"]["ShouYunJi"]["cookie"],
        )
    )["code"]
    == "11100"
), "cookie获取失败"


@alcommand(Alconna("兽兽"), private=False)
@decorate(GroupInterval.require(20, 3, send_alert=True))
async def random_furry(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    data = await spider.get_json("https://cloud.foxtail.cn/api/function/random")
    data2 = await spider.get_json(
        f'https://cloud.foxtail.cn/api/function/pictures?picture={data["picture"]["id"]}&model=1'
    )
    await app.send_message(
        friend,
        MessageChain(
            [
                Plain(f'名字:{data2["name"]}'),
                Image(**await spider.get_image(data2["url"]))
                if data["examine"] == 1 or data["url"] or data["url2"]
                else Plain("\n" + data2["msg"]),
                Plain(f'\nid:{data2["picture"]}'),
            ]
        ),
        quote=event.id,
    )


@alcommand(Alconna("兽兽{name}"), private=False)
@decorate(GroupInterval.require(20, 3, send_alert=True))
async def get_furry_by_name(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    try:
        data = (
            await spider.get_json(
                f'https://cloud.foxtail.cn/api/function/pulllist?name={result.header["name"]}'
            )
        )["open"]
        datat = choice(data)
        data2 = await spider.get_json(
            f'https://cloud.foxtail.cn/api/function/pictures?picture={datat["id"]}&model=1'
        )
        await app.send_message(
            friend,
            MessageChain(
                [
                    Plain(f'名字:{data2["name"]}'),
                    Image(**await spider.get_image(data2["url"]))
                    if data["examine"] == 1 or data["url"] or data["url2"]
                    else Plain("\n" + data2["msg"]),
                    Plain(f'\nid:{data2["picture"]}'),
                ]
            ),
            quote=event.id,
        )
    except IndexError:
        await app.send_message(
            friend, MessageChain([Plain("可能没有此兽xvx")]), quote=event.id
        )


@alcommand(Alconna("id为{id}的兽"), private=False)
@decorate(GroupInterval.require(10, 3, send_alert=True))
async def get_furry_by_id(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    if match(r"\d+", result.header["id"]) is not None:
        model = "1"
    else:
        model = "0"
    try:
        data = await spider.get_json(
            f'https://cloud.foxtail.cn/api/function/pictures?picture={result.header["id"]}&model={model}',
            sdata["cookie"],
        )
        await app.send_message(
            friend,
            MessageChain(
                [
                    Plain(f'名字:{data["name"]}'),
                    (
                        Image(**await spider.get_image(data["url"]))
                        if data["examine"] == 1 or data["url"] or data["url2"]
                        else Plain("\n" + data["msg"])
                    ),
                    Plain(f'\nid:{data["picture"]}'),
                ]
            ),
            quote=event.id,
        )
    except IndexError:
        await app.send_message(
            friend, MessageChain([Plain("可能没有此兽xvx")]), quote=event.id
        )


@alcommand(Alconna("上传兽云祭{name}", parse_prefix("ShouYunJi")), private=False)
@decorate(GroupInterval.require(10, 3, send_alert=True))
async def upload_shouyunji(
    app: Ariadne, friend: Friend | Group, result: Arparma, event: MessageEvent
):
    ret = result.header["name"]
    p = {"name": ret}

    # WAITER

    def waiter(
        waiter_message: MessageChain,
    ):
        return waiter_message[Image][0] if waiter_message.has(Image) else "ERROR"

    def waiter2(
        waiter_message: MessageChain,
    ):
        return waiter_message if waiter_message.display in ["0", "1", "2"] else "ERROR"

    def waiter3(
        waiter_message: MessageChain,
    ):
        if not waiter_message[Plain]:
            return "ERROR"
        return "EMPTY" if waiter_message.display == "无" else waiter_message.display

    await app.send_message(friend, Plain("[1/3]请发送一张图片"))
    # INIT IMG
    result_img = await FunctionWaiter(
        waiter,
        [GroupMessage],
        decorators=[CertainMember(event.sender.id, event.sender.group)],
        block_propagation=True,
    ).wait(timeout=30, default="ERROR")
    if result_img == "ERROR":
        await app.send_message(friend, Plain("超时或类型不对，取消操作"))
        return
    else:
        p["file"] = (await spider.get_image(result_img.url))["data_bytes"]
    await app.send_message(friend, Plain("[2/3]请发送类型数字\n0.设定 1.毛图  2.插画"))
    # INIT TYPE
    result_type = await FunctionWaiter(
        waiter2,
        [GroupMessage],
        decorators=[CertainMember(event.sender.id, event.sender.group)],
        block_propagation=True,
    ).wait(timeout=30, default="ERROR")
    if result_type == "ERROR":
        await app.send_message(friend, Plain("超时或类型不对，取消操作"), quote=event.id)
        return
    else:
        p["type"] = result_type.display
    # INIT TEXT
    await app.send_message(friend, Plain("[3/3]请发送介绍，不需要请发送无"))
    result_text = await FunctionWaiter(
        waiter3,
        [GroupMessage],
        decorators=[CertainMember(event.sender.id, event.sender.group)],
        block_propagation=True,
    ).wait(timeout=30, default="ERROR")
    if result_text == "ERROR":
        await app.send_message(friend, Plain("超时或类型不对，取消操作"), quote=event.id)
        return
    elif result_text != "EMPTY":
        p["suggest"] = result_text
    p["rem"] = f"由阿尔多泰上传。群：{event.sender.group.id},上传者：{event.sender.id}"
    p["power"] = "1"
    logger.info(p)
    rzt = await spider.post(
        "https://cloud.foxtail.cn/api/function/upload",
        kw=p,
        cookie=setting["plugin"]["ShouYunJi"]["cookie"],
    )
    await app.send_message(
        friend, rzt["msg"] + "\nuid:" + rzt["picture"] + "\nsid:" + rzt["id"]
    )


@alcommand(Alconna("上传兽云祭", parse_prefix("ShouYunJi")), private=False)
async def upload_shouyunji(app: Ariadne, friend: Friend | Group):
    await app.send_message(friend, "请发送！上传兽云祭<兽名称>")
