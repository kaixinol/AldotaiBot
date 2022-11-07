from graia.ariadne.event.mirai import MemberJoinEvent,NewFriendRequestEvent
from util.parseTool import *
from util.initializer import *
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel, Saya
from graia.ariadne.model import Friend, Group
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain,Plain
from graia.ariadne.app import Ariadne
import sys
from graia.ariadne.util.saya import decorate, dispatch, listen
import asyncio
from util.interval import GroupInterval

sys.path.append("../")


saya = Saya.current()
channel = Channel.current()


@listen(MemberJoinEvent)
@decorate(GroupInterval.require(1, 60*10))
async def setu(app: Ariadne, friend: Friend | Group, event: MemberJoinEvent):
    await app.send_message(
        friend,
        MessageChain("欢迎新成员，本bot使用方法请发送help。"),
    )

@channel.use(ListenerSchema(listening_events=[GroupMessage,FriendMessage]))
async def help(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if message.display.lower() in ["帮助","!帮助","！帮助","help"]:
        await app.send_message(
        friend,
        MessageChain("本bot文档地址：https://reset.forcecat.cn/（复制到浏览器后访问）"),
    )

@listen(NewFriendRequestEvent)
async def new_friend(app: Ariadne, event: NewFriendRequestEvent):
    """
    收到好友申请
    """
    await event.accept()
    await asyncio.sleep(10)
    await app.send_friend_message(event.supplicant, MessageChain(Plain('已通过你的好友申请')))
    return