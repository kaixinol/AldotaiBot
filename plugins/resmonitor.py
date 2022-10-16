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
from graia.ariadne.app import Ariadne
from graia.saya import Saya, Channel
from graia.saya.event import SayaModuleInstalled


saya = Saya.current()
channel = Channel.current()


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")

async def msg()->str:
    GB=1024*1024*1024
    m=''
    m+=f'CPU利用率：{psutil.cpu_percent(interval=1)}\n'
    m+=f'CPU核数：{psutil.cpu_count()}\n'
    m+=f'CPU MAX频率：{psutil.cpu_freq().max}MHz\n'
    m+=f'CPU 当前频率：{psutil.cpu_freq().current}MHz\n'
    m+=f'可用内存：{round(psutil.virtual_memory().available/GB,1)}GB\n'
    m+=f'可用磁盘容量：{round(psutil.disk_usage("/").free/GB,1)}GB\n'
    return m

@channel.use(ListenerSchema(listening_events=parseMsgType(ReadConfig('resmonitor'))))
async def setu(app: Ariadne, friend: Friend | Group,  event: MessageEvent):
    message = event.message_chain
    if len(message[Plain])==0:
        return
    from arclet.alconna import Alconna
    if Alconna("获取配置", headers=parsePrefix('resmonitor')).parse(message[Plain]).matched:
        data = await msg()
        await app.send_message(
            friend,
            MessageChain(Plain(data)),
        )
