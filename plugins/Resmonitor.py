import subprocess
import re
from util.parseTool import *
from util.initializer import *
from graia.saya.event import SayaModuleInstalled
from graia.saya import Channel, Saya
from graia.ariadne.model import Friend, Group
from graia.ariadne.message.element import Plain
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.event.message import GroupMessage, MessageEvent
from graia.ariadne.app import Ariadne
import psutil
import platform
import os
import sys

from graia.ariadne.util.saya import decorate, listen

sys.path.append("../")


saya = Saya.current()
channel = Channel.current()


async def get_processor_name():
    if platform.system() == "Windows":
        return subprocess.check_output('wmic CPU get NAME')[4:].decode().strip()
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


async def msg() -> str:
    GB = 1024 * 1024 * 1024
    return f"""
CPU名称：{await get_processor_name()}
CPU利用率：{psutil.cpu_percent(interval=1)}%
CPU 当前频率：{round(psutil.cpu_freq().current,1)}MHz
可用内存：{round(psutil.virtual_memory().available / GB,1)}GB
可用磁盘容量：{round(psutil.disk_usage("/").free / GB ,1)}GB
Python 版本：{platform.python_version()}
"""


@listen(GroupMessage)
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return

    from arclet.alconna import Alconna

    if Alconna("获取配置", headers=parsePrefix("Resmonitor")).parse(message[Plain]).matched:
        data = await msg()
        await app.send_message(
            friend,
            MessageChain(Plain(data)),
        )
