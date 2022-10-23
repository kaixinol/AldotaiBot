import sys
import os
sys.path.append('../')
from util.parseTool import *
from util.initializer import *
from graia.ariadne.message.element import (
    Image,
    Plain,
    At,
    Quote,
    AtAll,
    Face,
    Poke,
    Forward,
    App,
    Json,
    Xml,
    MarketFace,
)
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel
from graia.ariadne.model import Group, Friend
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage, FriendMessage, MessageEvent
from graia.ariadne.event.mirai import MemberJoinEvent
from graia.ariadne.app import Ariadne
from graia.saya import Saya, Channel
from graia.saya.event import SayaModuleInstalled
saya = Saya.current()
channel = Channel.current()
async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")
@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def setu(app: Ariadne, friend: Friend | Group,  event: MemberJoinEvent):
    await app.send_message(
                friend,
                MessageChain('欢迎新成员，本bot文档地址：https://botdoc-jlmo.vercel.app/'),
            )

