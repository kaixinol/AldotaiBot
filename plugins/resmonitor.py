import os
import sys

sys.path.append("../")
import psutil
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import FriendMessage, GroupMessage, MessageEvent
from graia.ariadne.message.chain import MessageChain
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
from graia.ariadne.model import Friend, Group
from graia.saya import Channel, Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.saya.event import SayaModuleInstalled

from util.initializer import *
from util.parseTool import *

saya = Saya.current()
channel = Channel.current()
import platform
import re
import subprocess


async def get_processor_name():
    if platform.system() == "Windows":
        return platform.processor()
    elif platform.system() == "Darwin":
        os.environ["PATH"] = os.environ["PATH"] + os.pathsep + "/usr/sbin"
        command = "sysctl -n machdep.cpu.brand_string"
        return subprocess.check_output(command).strip()
    elif platform.system() == "Linux":
        command = "cat /proc/cpuinfo"
        all_info = subprocess.check_output(command, shell=True).decode().strip()
        for line in all_info.split("\n"):
            if "model name" in line:
                return re.sub(".*model name.*:", "", line, 1)
    return ""


async def module_listener(event: SayaModuleInstalled):
    print(f"{event.module}::模块加载成功!!!")


async def msg() -> str:
    GB = 1024 * 1024 * 1024
    m = f"""
CPU名称：{await get_processor_name()}\n
CPU利用率：{psutil.cpu_percent(interval=1)}%\n
CPU 当前频率：{psutil.cpu_freq().current}MHz\n
可用内存：{round(psutil.virtual_memory().available/GB,1)}GB\n
可用磁盘容量：{round(psutil.disk_usage("/").free/GB,1)}GB
"""
    return m


@channel.use(ListenerSchema(listening_events=parseMsgType("resmonitor")))
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    from arclet.alconna import Alconna

    if Alconna("获取配置", headers=parsePrefix("resmonitor")).parse(message[Plain]).matched:
        data = await msg()
        await app.send_message(
            friend,
            MessageChain(Plain(data)),
        )
