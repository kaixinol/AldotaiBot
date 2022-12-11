import os
import platform
import re
import subprocess
import sys

import psutil
from graia.ariadne.app import Ariadne
from graia.ariadne.event.message import MessageEvent
from graia.ariadne.message.chain import MessageChain
from graia.ariadne.message.element import Plain
from graia.ariadne.model import Friend, Group
from graia.ariadne.util.saya import listen
from graia.saya import Channel, Saya

from util.parseTool import *
from arclet.alconna import Alconna


saya = Saya.current()
channel = Channel.current()


async def get_processor_name():
    if platform.system() == "Windows":
        return subprocess.check_output("wmic CPU get NAME")[4:].decode().strip()
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
    gb = 1024 * 1024 * 1024
    return f"""
CPU名称：{await get_processor_name()}
CPU利用率：{psutil.cpu_percent(interval=1)}%
CPU 当前频率：{round(psutil.cpu_freq().current, 1)}MHz
可用内存：{round(psutil.virtual_memory().available / gb, 1)}GB
可用磁盘容量：{round(psutil.disk_usage("/").free / gb, 1)}GB
程序已使用内存：{round(psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2, 1)}MB
Python 版本：{platform.python_version()}
"""


alcn = Alconna("获取配置", parse_prefix("Resmonitor"))


@listen(GroupMessage)
async def setu(app: Ariadne, friend: Friend | Group, event: MessageEvent):
    message = event.message_chain
    if len(message[Plain]) == 0:
        return
    if alcn.parse(message[Plain]).matched:
        data = await msg()
        await app.send_message(
            friend,
            MessageChain(Plain(data)),
        )
