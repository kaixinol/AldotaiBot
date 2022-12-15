import asyncio

from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.event.mirai import MemberJoinEvent, NewFriendRequestEvent
from graia.ariadne.message.chain import MessageChain, Plain
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.saya import decorate, listen
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema

from util.interval import GroupInterval
from util.parseTool import *

saya = Saya.current()
channel = Channel.current()


@listen(MemberJoinEvent)
@decorate(GroupInterval.require(60 * 3, 2, send_alert=False))
async def setu(app: Ariadne, friend: Friend | Group):
    await app.send_message(
        friend,
        MessageChain("欢迎新成员，本bot使用方法请发送help。"),
    )


@channel.use(ListenerSchema(listening_events=[GroupMessage, FriendMessage]))
async def get_help_doc(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if message.display.lower() in [
        "帮助",
        "!帮助",
        "！帮助",
        "help",
        ".help",
        ".帮助",
    ]:
        await app.send_message(
            friend,
            MessageChain("本bot文档地址：reset.forcecat.cn（复制到浏览器后访问）"),
        )


@listen(NewFriendRequestEvent)
async def new_friend(app: Ariadne, event: NewFriendRequestEvent):
    await event.accept()
    await asyncio.sleep(10)
    await app.send_friend_message(event.supplicant, MessageChain(Plain("已通过你的好友申请")))
