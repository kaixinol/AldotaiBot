from re import match
from asyncio import get_event_loop

from arclet.alconna import Alconna
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent, GroupMessage, FriendMessage
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group, MemberPerm
from graia.ariadne.util.saya import listen
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger as l

from util.initializer import setting, keyword
from util.parseTool import parse_prefix
from util.spider import Session
from arclet.alconna.graia import alcommand
from arclet.alconna import Alconna, Args, Arparma, MultiVar
from graia.ariadne.util.saya import decorate, dispatch, listen
from util.interval import GroupInterval
from util.parseTool import get_id

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
bot_list = set([i["id"] for i in raw_json])
l.info("bot 列表初始化完毕")
l.info(bot_list)


@listen(GroupMessage, FriendMessage)
async def answer(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain

    def get_qq_name(obj):
        return obj.nickname if hasattr(obj, "nickname") else obj.name

    if (
        not message[Plain]
        or message.display[:1] in ["!", "！"]
        or event.sender.id == app.account
        or "Aldotai" in get_qq_name(event.sender)
        or get_id(event.sender) in keyword
        or get_id(event.sender) in bot_list
    ):
        return
    for i in data["react"]:
        if i[0].startswith("regex:"):
            if (
                match(i[0].replace("regex:", ""), event.message_chain.display)
                is not None
            ):
                await app.send_message(friend, i[1])
                return
        if i[0].find(":") == -1 and i[0] in event.message_chain.display:
            await app.send_message(friend, i[1])
            return


@alcommand(Alconna("关键字开关", parse_prefix("KeywordAnswer")), private=True)
async def configure(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    if (
        event.sender.permission != MemberPerm.Member
        or get_id(event.sender) in setting["admins"]
    ):
        if get_id(event.sender) in keyword:
            keyword.pop(keyword.index(get_id(event.sender)))
            send = "已开启关键字回复"
        else:
            keyword.append(get_id(event.sender))
            send = "已关闭关键字回复"
    else:
        send = "你非管理员"
    await app.send_message(
        friend,
        MessageChain(send),
    )
