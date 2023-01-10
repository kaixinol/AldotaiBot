from asyncio import get_event_loop
from random import choice
from re import match

from arclet.alconna import Alconna
from arclet.alconna.graia import alcommand
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group, MemberPerm
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from loguru import logger

from util.initializer import keyword, setting
from util.parseTool import parse_prefix
from util.spider import Session

channel = Channel.current()

data = setting["plugin"]["KeywordAnswer"]
alcn = {
    i[0]: Alconna(i[0].replace("Alconna:", ""))
    for i in data["react"]
    if i[0].startswith("Alconna:")
}
spider = Session("keywordanswer", proxy=True)
loop = get_event_loop()
raw_json = loop.run_until_complete(
    spider.get_json(
        "https://raw.githubusercontent.com/FurDevsCN/furry-bot-list/main"
        "/JSON/bot.json"
    )
)
bot_list = {i["id"] for i in raw_json}
logger.info("bot 列表初始化完毕")
logger.info(bot_list)


def get_qq_name(obj):
    return obj.nickname if hasattr(obj, "nickname") else obj.name


@listen(GroupMessage)
async def answer_group(app: Ariadne, friend: Group, event: MessageEvent):
    message = event.message_chain
    if (
        not message[Plain]
        or message.display[:1] in ["!", "！"]
        or "Aldotai" in get_qq_name(event.sender)
        or event.sender.group.id in keyword
        or event.sender.id in bot_list
    ):
        return
    for i, msg in data["react"]:
        if (
            i.startswith("regex:")
            and match(i.replace("regex:", ""), event.message_chain.display)
            is not None
        ):
            if not isinstance(msg, list):
                await app.send_message(friend, msg)
            else:
                await app.send_message(friend, choice(msg))
            return
        if i.find(":") == -1 and i in event.message_chain.display:
            if not isinstance(msg, list):
                await app.send_message(friend, msg)
            else:
                await app.send_message(friend, choice(msg))
            return


@listen(FriendMessage)
async def answer(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if (
        not message[Plain]
        or message.display[:1] in ["!", "！"]
        or event.sender.id == app.account
    ):
        return
    for i, msg in data["react"]:
        if (
            i.startswith("regex:")
            and match(i.replace("regex:", ""), event.message_chain.display)
            is not None
        ):
            if not isinstance(msg, list):
                await app.send_message(friend, msg)
            else:
                await app.send_message(friend, choice(msg))
            return
        if i.find(":") == -1 and i in event.message_chain.display:
            if not isinstance(msg, list):
                await app.send_message(friend, msg)
            else:
                await app.send_message(friend, choice(msg))
            return


@alcommand(Alconna("关键字开关", parse_prefix("KeywordAnswer")), private=False)
async def configure(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    if (
        event.sender.id in setting["admins"]
        or event.sender.permission != MemberPerm.Member
    ):
        if event.sender.group.id in keyword:
            keyword.pop(keyword.index(event.sender.group.id))
            send = "已开启关键字回复"
        else:
            keyword.append(event.sender.group.id)
            send = "已关闭关键字回复"
    else:
        send = "你非管理员"
    await app.send_message(
        friend,
        MessageChain(send),
    )
