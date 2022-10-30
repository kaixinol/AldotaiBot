from graia.ariadne.event.mirai import MemberJoinEvent
from util.parseTool import *
from util.initializer import *
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya import Channel, Saya
from graia.ariadne.model import Friend, Group
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.app import Ariadne
import sys

sys.path.append("../")


saya = Saya.current()
channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MemberJoinEvent]))
async def setu(app: Ariadne, friend: Friend | Group, event: MemberJoinEvent):
    await app.send_message(
        friend,
        MessageChain("欢迎新成员，本bot文档地址：https://botdoc-jlmo.vercel.app/"),
    )
