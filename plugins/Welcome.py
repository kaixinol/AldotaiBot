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


sys.path.append("../")


saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def setu(app: Ariadne, friend: Friend | Group, event: MemberJoinEvent):
    await app.send_message(
        friend,
        MessageChain("欢迎新成员，本bot文档地址：https://reset.forcecat.cn/"),
    )

@channel.use(ListenerSchema(listening_events=[GroupMessage,FriendMessage]))
async def help(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if message.display.lower() in ["帮助","!帮助","！帮助","help"]:
        await app.send_message(
        friend,
        MessageChain("本bot文档地址：https://reset.forcecat.cn/"),
    )

@listen(NewFriendRequestEvent)
async def new_friend(app: Ariadne, event: NewFriendRequestEvent):
    """
    收到好友申请
    """
    await event.accept()
    await app.send_friend_message(event.supplicant, MessageChain(Plain('已通过你的好友申请')))
    return