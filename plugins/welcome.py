from graia.ariadne.event.mirai import MemberJoinEvent, MemberCardChangeEvent
from util.parseTool import *
from util.initializer import *
from graia.saya.event import SayaModuleInstalled
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel, Saya
from graia.ariadne.model import Friend, Group
from graia.ariadne.message.element import (
    App,
    At,
    AtAll,
    Face,
    Forward,
    Image,
    Json,
    MarketFace,
    Plain,
    Poke,
    Quote,
    Xml,
)
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.app import Ariadne
import os
import sys

sys.path.append("../")


saya = Saya.current()
channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def setu(app: Ariadne, friend: Friend | Group, event: MemberJoinEvent):
    await app.send_message(
        friend,
        MessageChain("欢迎新成员，本bot文档地址：https://botdoc-jlmo.vercel.app/"),
    )


@channel.use(ListenerSchema(listening_events=[MemberCardChangeEvent]))
async def setu(app: Ariadne, friend: Friend | Group, event: MemberCardChangeEvent):
    if 'stop' in event.current.lower():
        await app.send_message(
            friend,
            MessageChain("Bot全局终止"),
        )
        app.stop()
